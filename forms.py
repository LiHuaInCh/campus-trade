from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo


class RegisterForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired("请输入用户名"), Length(2, 50)])
    password = PasswordField("密码", validators=[DataRequired("请输入密码"), Length(6, 128)])
    confirm = PasswordField("确认密码", validators=[
        DataRequired("请确认密码"),
        EqualTo("password", "两次密码不一致")
    ])
    phone = StringField("手机号", validators=[DataRequired("请输入手机号"), Length(6, 20)])


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired("请输入用户名")])
    password = PasswordField("密码", validators=[DataRequired("请输入密码")])


class ProductForm(FlaskForm):
    title = StringField("商品名称", validators=[DataRequired("请输入商品名称"), Length(1, 100)])
    description = TextAreaField("商品描述", validators=[DataRequired("请输入商品描述")])
    price = FloatField("价格", validators=[DataRequired("请输入价格"), NumberRange(0.01, 99999)])
    category = SelectField("分类", choices=[
        ("书籍", "书籍"),
        ("电子产品", "电子产品"),
        ("生活用品", "生活用品"),
        ("衣物", "衣物"),
        ("运动器材", "运动器材"),
        ("其他", "其他"),
    ], validators=[DataRequired("请选择分类")])


class MessageForm(FlaskForm):
    content = TextAreaField("留言内容", validators=[DataRequired("请输入留言内容"), Length(1, 500)])


class PrivateMessageForm(FlaskForm):
    content = TextAreaField("私信内容", validators=[DataRequired("请输入私信内容"), Length(1, 500)])
