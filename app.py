import os
import uuid
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Product, Message, PrivateMessage, CartItem
from forms import RegisterForm, LoginForm, ProductForm, MessageForm, PrivateMessageForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "campus-trade-secret-key-2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trade.db"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "static/uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "请先登录"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_admin():
    """启动时自动创建管理员账户"""
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", phone="10000000000", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()


# ==================== 上下文注入 ====================

@app.context_processor
def inject_unread():
    """向所有模板注入未读私信数和购物车数量"""
    data = {"unread_count": 0, "cart_count": 0}
    if current_user.is_authenticated:
        data["unread_count"] = PrivateMessage.query.filter_by(
            receiver_id=current_user.id, is_read=False
        ).count()
        data["cart_count"] = CartItem.query.filter_by(user_id=current_user.id).count()
    return data


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== 欢迎首页 ====================

@app.route("/")
def home():
    latest = Product.query.filter_by(status="在售").order_by(Product.created_at.desc()).limit(8).all()
    return render_template("home.html", latest=latest)


# ==================== 商品浏览（原首页） ====================

@app.route("/browse")
def browse():
    keyword = request.args.get("q", "")
    category = request.args.get("category", "")
    sort = request.args.get("sort", "newest")
    price_min = request.args.get("price_min", "")
    price_max = request.args.get("price_max", "")

    query = Product.query.filter_by(status="在售")

    if keyword:
        query = query.filter(
            Product.title.contains(keyword) | Product.description.contains(keyword)
        )
    if category:
        query = query.filter_by(category=category)
    if price_min:
        try:
            query = query.filter(Product.price >= float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            query = query.filter(Product.price <= float(price_max))
        except ValueError:
            pass

    # 排序
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.all()

    # 统计数据
    stats = {
        "product_count": Product.query.filter_by(status="在售").count(),
        "user_count": User.query.count(),
    }

    has_filter = keyword or category or price_min or price_max or (sort != "newest")

    return render_template(
        "browse.html",
        products=products,
        keyword=keyword,
        category=category,
        sort=sort,
        price_min=price_min,
        price_max=price_max,
        stats=stats,
        has_filter=has_filter,
    )


# ==================== 注册 ====================

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("用户名已存在", "danger")
            return render_template("register.html", form=form)

        user = User(username=form.username.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("注册成功，请登录", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


# ==================== 登录 ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("用户名或密码错误", "danger")
            return render_template("login.html", form=form)

        login_user(user)
        flash("登录成功", "success")
        return redirect(url_for("home"))
    return render_template("login.html", form=form)


# ==================== 退出登录 ====================

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("home"))


# ==================== 发布商品 ====================

@app.route("/publish", methods=["GET", "POST"])
@login_required
def publish():
    form = ProductForm()
    if form.validate_on_submit():
        image = request.files.get("image")
        filename = "default.jpg"
        if image and image.filename and allowed_file(image.filename):
            ext = image.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        product = Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            image=filename,
            seller_id=current_user.id,
        )
        db.session.add(product)
        db.session.commit()
        flash("发布成功", "success")
        return redirect(url_for("browse"))
    return render_template("publish.html", form=form)


# ==================== 商品详情 + 留言 ====================

@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    message_form = MessageForm()

    if message_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("请先登录", "warning")
            return redirect(url_for("login"))

        message = Message(
            content=message_form.content.data,
            product_id=product.id,
            user_id=current_user.id,
        )
        db.session.add(message)
        db.session.commit()
        flash("留言成功", "success")
        return redirect(url_for("product_detail", product_id=product.id))

    messages = (
        Message.query.filter_by(product_id=product.id)
        .order_by(Message.created_at.desc())
        .all()
    )
    return render_template(
        "product_detail.html", product=product, message_form=message_form, messages=messages
    )


# ==================== 购买商品 ====================

@app.route("/product/<int:product_id>/buy", methods=["POST"])
@login_required
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id == current_user.id:
        flash("不能购买自己的商品", "warning")
        return redirect(url_for("product_detail", product_id=product.id))

    if product.status == "已售":
        flash("该商品已售出", "warning")
        return redirect(url_for("product_detail", product_id=product.id))

    product.status = "已售"
    # 从购物车中移除该商品
    CartItem.query.filter_by(product_id=product.id).delete()
    db.session.commit()
    flash("购买成功", "success")
    return redirect(url_for("product_detail", product_id=product.id))


# ==================== 我发布的商品 ====================

@app.route("/my-products")
@login_required
def my_products():
    products = (
        Product.query.filter_by(seller_id=current_user.id)
        .order_by(Product.created_at.desc())
        .all()
    )
    return render_template("my_products.html", products=products)


# ==================== 购物车 ====================

@app.route("/cart")
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).order_by(CartItem.created_at.desc()).all()
    return render_template("cart.html", items=items)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def cart_add(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id == current_user.id:
        flash("不能添加自己的商品到购物车", "warning")
        return redirect(url_for("product_detail", product_id=product.id))

    if product.status == "已售":
        flash("该商品已售出", "warning")
        return redirect(url_for("product_detail", product_id=product.id))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if existing:
        flash("该商品已在购物车中", "info")
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=product.id))
        db.session.commit()
        flash("已加入购物车", "success")
    return redirect(url_for("product_detail", product_id=product.id))


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def cart_remove(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("无权操作", "danger")
        return redirect(url_for("cart"))
    db.session.delete(item)
    db.session.commit()
    flash("已从购物车移除", "info")
    return redirect(url_for("cart"))


# ==================== 私信 ====================

@app.route("/messages")
@login_required
def messages():
    # 找到所有与我有过私信的用户（按最新消息排序）
    sent = db.session.query(PrivateMessage.receiver_id).filter_by(sender_id=current_user.id).distinct()
    received = db.session.query(PrivateMessage.sender_id).filter_by(receiver_id=current_user.id).distinct()

    partner_ids = set()
    for (pid,) in sent:
        partner_ids.add(pid)
    for (pid,) in received:
        partner_ids.add(pid)

    partners = []
    for pid in partner_ids:
        partner = User.query.get(pid)
        # 该对话的未读数
        unread = PrivateMessage.query.filter_by(
            sender_id=pid, receiver_id=current_user.id, is_read=False
        ).count()
        # 最后一条消息时间
        last_msg = PrivateMessage.query.filter(
            ((PrivateMessage.sender_id == current_user.id) & (PrivateMessage.receiver_id == pid))
            | ((PrivateMessage.sender_id == pid) & (PrivateMessage.receiver_id == current_user.id))
        ).order_by(PrivateMessage.created_at.desc()).first()

        partners.append({
            "user": partner,
            "unread": unread,
            "last_time": last_msg.created_at if last_msg else None,
        })

    partners.sort(key=lambda x: x["last_time"] or "", reverse=True)
    return render_template("messages.html", partners=partners)


@app.route("/messages/<int:partner_id>", methods=["GET", "POST"])
@login_required
def conversation(partner_id):
    if partner_id == current_user.id:
        flash("不能给自己发私信", "warning")
        return redirect(url_for("messages"))

    partner = User.query.get_or_404(partner_id)
    form = PrivateMessageForm()

    if form.validate_on_submit():
        msg = PrivateMessage(
            content=form.content.data,
            sender_id=current_user.id,
            receiver_id=partner.id,
        )
        db.session.add(msg)
        db.session.commit()
        flash("发送成功", "success")
        return redirect(url_for("conversation", partner_id=partner.id))

    # 标记对方发来的消息为已读
    PrivateMessage.query.filter_by(
        sender_id=partner.id, receiver_id=current_user.id, is_read=False
    ).update({"is_read": True})
    db.session.commit()

    # 获取两人之间的所有消息
    msgs = PrivateMessage.query.filter(
        ((PrivateMessage.sender_id == current_user.id) & (PrivateMessage.receiver_id == partner.id))
        | ((PrivateMessage.sender_id == partner.id) & (PrivateMessage.receiver_id == current_user.id))
    ).order_by(PrivateMessage.created_at.asc()).all()

    return render_template("conversation.html", partner=partner, form=form, msgs=msgs)


# ==================== 管理后台 ====================

@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        flash("无权访问管理后台", "danger")
        return redirect(url_for("home"))

    users = User.query.order_by(User.created_at.desc()).all()
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin.html", users=users, products=products)


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        flash("无权操作", "danger")
        return redirect(url_for("home"))

    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("不能删除管理员", "warning")
        return redirect(url_for("admin"))

    # 删除该用户相关的数据
    PrivateMessage.query.filter(
        (PrivateMessage.sender_id == user.id) | (PrivateMessage.receiver_id == user.id)
    ).delete()
    CartItem.query.filter_by(user_id=user.id).delete()
    Message.query.filter_by(user_id=user.id).delete()
    Product.query.filter_by(seller_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f"已删除用户 {user.username}", "success")
    return redirect(url_for("admin"))


@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@login_required
def admin_delete_product(product_id):
    if not current_user.is_admin:
        flash("无权操作", "danger")
        return redirect(url_for("home"))

    product = Product.query.get_or_404(product_id)
    CartItem.query.filter_by(product_id=product.id).delete()
    Message.query.filter_by(product_id=product.id).delete()
    db.session.delete(product)
    db.session.commit()
    flash(f"已删除商品 {product.title}", "success")
    return redirect(url_for("admin"))


# ==================== 启动 ====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True, port=5000)
