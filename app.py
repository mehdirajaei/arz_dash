from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# List of Persian item names
PERSIAN_ITEMS = [
    "تعداد کل دانشجویان (آزاد و غیر آزاد) شهر/ استان",
    "تعداد کل اعضای هیات علمی",
    "تعداد کل دستیاران آموزشی",
    "تعداد کل اعضای هیات علمی وابسته",
    "تعداد کل مدرسان حق التدریس",
    "تعداد اعضای هیات علمی سرآمد علمی",
    "تعداد اعضای هیات علمی فناور برتر (سرآمد فناوری)",
    "تعداد دانشجویان دارای فعالیت علمی ماندگار و اثرگذار",
    "درآمد (میانگین درآمد) دانشجویان دانشگاه از طریق انجام پروژه ها",
    "تعداد کل دانشجویان شاغل",
    "تعداد کل دانشجویان شاغل مرتبط با رشته تحصیلی",
    "تعداد دانشجویان شاغل در فعالیت های علمی، پژوهشی و دانش بنیان",
    "تعداد دانش آموختگان شاغل در فعالیت های علمی، پژوهشی و دانش بنیان",
    "تعداد اختراعات ثبت شده توسط دانشجویان در مدت تحصیل",
    "تعداد روش های نوآورانه ثبت شده توسط دانشجویان",
    "تعداد ایده های نوآورانه و اختراعات اعضای باشگاه پژوهشگران جوان و نخبگان",
    "تعداد کل پژوهش ها در بازه ارزیابی شهریور 1402 تا پایان مرداد 1403",
    "تعداد پژوهش های منجر به راه حل شده مورد پذیرش ذینفعان در بازه ارزیابی",
    "تعداد کل مسائل ثبت شده توسط اعضای هیات علمی",
    "تعداد مسائل کشف شده توسط هسته های فکری کاشف فناور",
    "تعداد همایش ها مرتبط با ارتباطات پایدار واحد دانشگاهی با مدیران دولتی و فعالان اجتماعی، اقتصادی و سیاسی محلی",
    "تعداد جلسات مرتبط با ارتباطات پایدار واحد دانشگاهی با مدیران دولتی و فعالان اجتماعی، اقتصادی و سیاسی محلی",
    "درآمدهای ناخالص پژوهشی و آزمایشگاهی در طول سال مالی(هزار ریال)",
    "هزینه های عملیاتی ناشی از فعالیت های پژوهشی و آزمایشگاهی در طول یک سال مالی (هزار ریال)",
    "درآمدهای حاصل از فروش داده، اختراعات و قراردادهای دانش فنی در طول سال مالی(هزار ریال)",
    "درآمد حاصل از جذب سرمایه گذاری، فروش محصول یا خدمات فناورانه، عارضه یابی و انتقال فناوری",
    "درآمدهای حاصل از حمایت بهره برداران از پایان نامه ها و رساله ها",
    "درآمدهای حاصل از فروش داده، فعالیت های کاربنیان در طول سال مالی",
    "درآمدهای حاصل از  مدارس عالی مهارتی در طول سال مالی",
    "درآمدهای ناخالص پژوهشی (فناوری و مهارتی) دانشگاه",
    "تعداد کل مقالات منتشر شده توسط دانشجویان دکتری در بازه ارزیابی",
    "تعداد کل اختراعات داخلی توسط اعضاء هیات علمی دانشگاه",
    "تعداد کل ثبت پتنت بین المللی أعضاء هیات علمی دانشگاه",
    "تعداد کل اعضای هیات علمی علوم انسانی",
    "تعداد مقالات یک درصد برتر (سایت اسکور) در سال 2023",
    "اچ ایندکس",
    "تعداد استناد به ازای هر مقاله",
    "تعداد پروژه های پژوهشی و فناوری که بصورت مشترک با نهادهای بین المللی و یا برای آن ها انجام شده است.",
    "تعداد پایان نامه ها و رساله های منجر به پژوهش جدید شده",
    "تعداد پایان نامه ها و رساله های منجر به قرارداد برون سازمانی",
    "تعداد پایان نامه ها و رساله های تعریف شده منطبق بر مسائل واقعی در بازه ارزیابی",
    "تعداد پژوهش های منجر به نوآوری شده در بازه ارزیابی",
    "تعداد پژوهش های تبدیل شده به فناوری کاربردی",
    "تعداد فناوری های تولید شده از مهر سال 1400",
    "تعداد کل فناوریهای تجاری شده از مهر 1400 تا کنون",
    "تعداد کل تولیدات علمی",
    "تعداد دانشجویان تحصیلات تکمیلی دارای نوآوری به ثبت رسیده بازه ارزیابی یکساله",
    "تعدا اختراعاتی که از پایان نامه های ارشد و دکترا مستخرج شده است.",
    "تعداد قراردادهای انجام پژوهش کاربردی، انجام خدمات فنی، جذب سرمایه گذاری، فروش محصول یا خدمات فناورانه، عارضه یابی و انتقال فناوری در سال مالی 1402-1403",
    "تعداد قراردادهای انجام پژوهش کاربردی، انجام خدمات فنی، جذب سرمایه گذاری، فروش محصول یا خدمات فناورانه، عارضه یابی و انتقال فناوری در سال مالی 1401-1402",
    "تعداد قراردادهای انجام پژوهش کاربردی، انجام خدمات فنی، جذب سرمایه گذاری، فروش محصول یا خدمات فناورانه، عارضه یابی و انتقال فناوری در سال مالی 1400-1401",
    "تعداد واحدهای فناور، نوآور و کسب و کارهای دانش بنیان واحد / استان",
    "تعداد دانشجویان عضو فعال در واحدهای نوآور، فناور و شرکت های دانش بنیان واحد / استان",
    "تعداد دانش آموختگان دانشگاه آزاد عضو فعال در واحدهای نوآور، فناور و شرکت های دانش بنیان واحد / استان",
    "تعداد اعضای هیات علمی فعال در واحدهای نوآور، فناور و شرکت های دانش بنیان واحد / استان",
    "تعداد شرکت های فناور، دانش بنیان و خلاق تحت پوشش سراهای نوآوری و پارک علم و فناوری واحد",
    "تعداد کل شرکت های زایشی از مهر 1400 تا کنون",
    "تعداد کل شرکت های زایشی که به موقعیت برتر کشب و کار رسیده اند. در بازه مهر 1400 تا کنون)",
    "تعداد کل فعالیت های مشترک با نهادهای معتبر بین المللی",
    "تعداد فعالیت های مشترک با نهادهای معتبر بین المللی که دارای حجم مالی بیش از 10 هزار دلار هستند",
    "رتبه H-index واحد / استان در سال 2022",
    "رتبه H-index واحد / استان در سال 2023",
    "تعداد دانشجویان با تراز بالای 95 درصد، که در سال تحصیلی 1402-1403 در واحد دانشگاهی ثبت نام نموده اند.",
    "تعداد دانشجویان تحصیلات تکمیلی ورودی 1402-1403 که در مقطع پایه فارغ التحصیل دانشگاه آزاد اسلامی می باشند",
    "تعداد مقالات داغ و پراستناد منتشر شده برتر",
    "تعداد مقالات منتشر شده در ده نشریه برتر بین المللی (نیچر، ساینس، لنست،...)",
    "تعداد کتاب های تالیف شده توسط اعضای هیات علمی",
    "تعداد اقدامات شاخص در حوزه تمدن آفرینی اسلامی",
    "تعداد کل پژوهشها در حوزه علوم انسانی در بازه ارزیابی",
    "تعداد کل مقالات معتبر علوم انسانی در بازه ارزیابی",
    "تعداد مطالعات مستند به منابع اسلامی و یا دربردارنده نفوذ اصول حکمت اسلامی در سایر علوم",
    "تعداد پژوهش های منجر به راه حل کاربردی شده با استفاده از علوم انسانی اسلامی",
    "تعداد کل پژوهش های علوم انسانی با موضوع علوم اسلامی",
    "تعداد مقالات با ضریب تاثیر بالا در حوزه علوم انسانی مبتنی بر معارف اسلامی و یا با استفاده از منابع اسلامی",
    "تعداد کل کارمندان (کارکنان غیر عضو هیات علمی)",
    "تعداد پرونده های تخلف اداری (در بازه ارزیابی)",
    "میزان کل درآمد (هزار ریال)",
    "میزان کل درآمد شهریه ای (هزار ریال)",
    "میزان کل درآمد غیر شهریه ای (بجز محل فروش یا انتقال دارایی)",
    "میزان کل درآمد از محل فروش یا انتقال دارایی",
    "میزان درآمد ناشی از طرح ها و قراردادهای برون دانشگاهی",
    "میزان درآمد از آموزش های کوتاه مدت کاربردی",
    "میزان درآمد ناشی از اعتبارات مردمی و کمک سازمان ها و امور خیریه",
    "میزان درآمد ناخالص ناشی از خدمات پزشکی و پیراپزشکی و بیمارستانها",
    "میزان درآمد خالص ناشی از خدمات پزشکی و پیراپزشکی و بیمارستانها",
    "مساحت کل املاک و مستغلات  (متر مربع)",
    "مساحت املاک و مستغلات در حال استفاده و بهسازی شده (مترمربع)",
    "مساحت املاک و مستغلات مولد سازی شده بر حسب متر مربع در بازه سال مالی 1402-1403",
    "میزان درآمد ناخالص در سال مالی 1401-1402(هزار ریال)",
    "میزان درآمد کل دانشگاه در سال مالی 1400-1401(هزار ریال)",
    "مجموع حقوق پرداختی به اعضای هیات علمی",
    "مجموع حقوق پرداختی به کارکنان (غیر عضو هیات علمی)",
    "میزان کل حق مدیریت و سرپرستی پرداخت شده (مدیریت علمی، اداری و اثر بخشی)",
    "میزان کل هزینه های دانشگاه در سال مالی 1402-1403(هزار ریال)",
    "میزان کل هزینه های غیر پرسنلی",
    "ارزش برآوردی دارایی ها",
    "تعداد گروههای کاری و علمی که اعضای هیات علمی در آنها عضو هستند",
    "تعداد اعضای هیات علمی عضو شبکه های کاری و تحقیقاتی و علمی",
    "تعداد فعالیتهای علمی مشترک با واحدهای دانشگاهی دیگر در بازه ارزیابی",
    "تعداد فعالیتهای بین المللی مشترک در بازه ارزیابی",
    "تعداد تشکل ها و گروههای دانشجویی و اساتید جهادی، خیرخواهانه و داوطلبانه",
    "تعداد کل دانشجویان",
    "تعداد کل دانشجویان فعال",
    "تعداد کل دانشجویان غیرفعال",
    "تعداد کل دانشجویان فعال کاردانی",
    "تعداد کل دانشجویان فعال کارشناسی",
    "تعداد کل دانشجویان فعال دکترای تخصصی",
    "تعداد کل دانشجویان فعال دکتری حرفه ای",
    "تعداد کل دانشجویان فعال پیراپزشکی",
    "تعداد کل دانشجویان غیرایرانی",
    "تعداد کل دانشجویان فعال غیرایرانی",
    "تعداد کل دانشجویان فعال غیرایرانی - غیرمقیم",
    "تعداد کل پذیرفته شدگان ورودی مهر1402",
    "تعداد کل ثبت نام کنندگان مهر1402",
    "تعداد کل دانشجویان پذیرفته شده ورودی بهمن 1402",
    "تعداد کل ثبت نام کنندگان بهمن1402",
    "تعداد کل دانش آموختگان از ابتدای تاسیس واحد",
    "تعداد کل دانش آموختگان از شهریور 1399 تا مرداد 1403",
    "تعداد کل دانش آموختگان در سال مالی 1402 -1403",
    "تعداد کل رشته های تحصیلی",
    "تعداد رشته های دارای مطلوبیت اقتضایی",
    "تعداد رشته های دارای جذابیت اجتماعی",
    "تعداد رشته های در حال بررسی",
    "تعداد رشته های غیر پویا",
    "تعداد کل مدارس",
    "تعداد مدارس تاسیس شده در بازه سال مالی 1402-1403",
    "تعداد کل دانش آموزان سما در خرداد 1403",
    "تعداد کل دانش آموزان سما در خرداد 1402",
    "تعداد کل دانش آموزان پیش دبستانی در خرداد 1403",
    "تعداد کل دانش آموزان مقطع ابتدایی در خرداد 1403",
    "تعداد کل دانش آموزان مقطع متوسطه اول در خرداد 1403",
    "تعداد کل دانش آموزان مقطع متوسطه دوم در خرداد 1403",
    "تعداد کل معلمان رسمی",
    "تعداد کل معلمان حق التدریس مدارس سما",
    "تعداد کل کادر اداری مدارس (بدون معلم)",
    "تعداد دانش آموختگان در جایگاه های برتر علمی، اجتماعی، فرهنگی، اقتصادی و یا مدیریتی",
    "نظر سنجی در دوره ی مورد نظر از کارفرما درباره کیفیت کاری دانش آموختگان دانشگاه",
    "تعداد دانش آموختگان دارای فعالیت علمی ماندگار و اثرگذار",
    "میانگین درآمد دانش آموختگان دانشگاه",
    "حداقل حقوق مصوب کشوری",
    "تعداد دانش آموختگان شاغل در رشته مرتبط",
    "تعداد دانش آموختگان شاغل",
    "امتیاز شاخص های کلیدی عملکرد مدارس سما در سال 1401-1402",
    "امتیاز شاخص های کلیدی عملکرد مدارس سما در سال 1402-1403",
    "تعداد دانش آموزانی که در یکی از حوزه های علمی، آموزشی، مهارتی، پژوهشی،فرهنگی و تربیت بدنی در بازه 1401-1402 سرآمد هستند",
    "تعداد دانش آموزانی که در یکی از حوزه های علمی، آموزشی، مهارتی، پژوهشی،فرهنگی و تربیت بدنی در سالتحصیلی 1402-1403 سرآمد هستند",
    "تعداد معلمان و عوامل مدرسه سرآمد در سالتحصیلی 1401-1402",
    "تعداد معلمان و عوامل مدرسه سرآمد در سالتحصیلی 1402-1403",
    "امتیاز عملکرد فرهنگی مدارس سما در سالتحصیلی 1401-1400",
    "امتیاز عملکرد فرهنگی مدارس سما در سالتحصیلی 1402-1401",
    "نفوذ فضائل اخلاقی و باورهای دینی و التزام به مسئولیت های اجتماعی",
    "نفوذ روحیه انقلابی، تعلق به آرمان های انقلاب و هویت ایرانی- اسلامی؛ ایثار و جهاد",
    "نفوذ فرهنگ عفاف و خانواده محوری",
    "نفوذ سبک زندگی اسلامی – ایرانی و روحیه قناعت و سخت کوشی",
    "نفوذ قانون مداری و خرد ورزی و اعتماد بنفس",
    "تعداد کل پایان نامه های کارشناسی ارشد دفاع شده در بازه ارزیابی",
    "تعداد کل رساله های دکترا دفاع شده در بازه ارزیابی",
    "تعداد کل دانشجویان فعال کارشناسی ارشد",
    "تعداد کل شرکت های دانش بنیان و خلاق (در کشور)",
    "رتبه واحد دانشگاهی در نظام رتبه بندی RUR یا شانگهای",
    "تعداد کل افرادی که سالتحصیلی 1402-1403 در واحد پذیرفته شده اند",
    "تعداد کل افرادی که سالتحصیلی 1402-1403 در واحد ثبت نام و انتخاب واحد کرده اند",
    "درصد ثبت نام از میان پذیرفته شدگان مقطع کاردانی",
    "درصد ثبت نام از میان پذیرفته شدگان مقطع کارشناسی",
    "درصد ثبت نام از میان پذیرفته شدگان مقطع کارشناسی ارشد",
    "درصد ثبت نام از میان پذیرفته شدگان مقطع دکترا",
    "اعتبار برند دانشگاه",
    "ارزیابی کفایت مدیریتی واحدهای دانشگاهی",
    "نظرسنجی پیرامون استقرار چرخه های یادگیری سازمانی",
    "ارزیابی بلوغ نظام اداری و مدیریتی واحدهای سازمان مرکزی",
    "میزان اطلاعات مالی دانشگاه که به اطلاع عموم می رسد.",
    "نرخ تورم در سال مد نظر",
    "GDP آموزش در سال 1401",
    "درآمد ناخالص مدارس سما در سال مالی 1401-1402 (هزار ریال)",
    "درآمد ناخالص مدارس سما در سال مالی 1402-1403 (هزار ریال)",
    "تعداد کل مدرسه سما در سال تحصیلی 1402-1403",
    "تعداد کل مدرسه سما در سال تحصیلی 1402-1401",
    "تعداد کل واحدهای دانشگاهی",
    "تعداد شبکه های کاری میان واحدهای مختلف",
    "موازی کاری غیر سازنده",
    "نفوذ روحیه انقلابی و بینش تمدنی",
    "خودباوری و احساس تعلق به دانشگاه",
    "نفوذ فرهنگ مشارکت و کارگروهی",
    "نفوذ قانونمداری، برنامه پذیری، سخت کوشی، امید، روحیه ایثار و جهاد"
]

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comment', backref='user', lazy=True)

class DataEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item = db.Column(db.String(1), nullable=False)  # A to Z
    value = db.Column(db.String(255))  # User input value
    document_path = db.Column(db.String(255))  # Path to uploaded document

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_comment = db.Column(db.Text, nullable=False)  # Comment from admin or user
    user_response = db.Column(db.Text)  # Response from user
    is_admin_comment = db.Column(db.Boolean, default=True)  # True for admin comments, False for user comments

# Create database tables
with app.app_context():
    db.create_all()

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'xlsx'}

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if admin
        if username == 'rajaei' and password == 'mehdisalmasi':
            session['user_id'] = 'admin'
            session['username'] = 'rajaei'
            return redirect(url_for('admin_dashboard'))
        
        # Check regular user
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login details', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session['user_id'] == 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/data_entry', methods=['GET', 'POST'])
def data_entry():
    if 'user_id' not in session or session['user_id'] == 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        for i, item in enumerate(PERSIAN_ITEMS, start=1):
            value = request.form.get(f'value_{i}')
            file = request.files.get(f'file_{i}')
            
            if value or file:
                existing_entry = DataEntry.query.filter_by(user_id=user.id, item=str(i)).first()
                if existing_entry:
                    existing_entry.value = value
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        existing_entry.document_path = file_path
                else:
                    data = DataEntry(user_id=user.id, item=str(i), value=value)
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        data.document_path = file_path
                    db.session.add(data)
        
        db.session.commit()
        flash('Data saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    existing_data = DataEntry.query.filter_by(user_id=user.id).all()
    data_dict = {int(entry.item): entry for entry in existing_data}  # Convert item to int for lookup
    
    return render_template('data_entry.html', data_dict=data_dict, persian_items=PERSIAN_ITEMS)

@app.route('/download_excel')
def download_excel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['user_id'] == 'admin':
        # Admin: Download all users' data
        users = User.query.all()
        data = []
        for user in users:
            entries = DataEntry.query.filter_by(user_id=user.id).all()
            for entry in entries:
                # Map item number to Persian name
                item_name = PERSIAN_ITEMS[int(entry.item) - 1]  # Subtract 1 because list is 0-indexed
                data.append({
                    'User': user.full_name,
                    'Item Number': entry.item,
                    'Item Name': item_name,  # Add Persian item name
                    'Value': entry.value,
                    'Document': entry.document_path if entry.document_path else 'No Document'
                })
        
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='All Data')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='all_users_data.xlsx'
        )
    else:
        # Regular user: Download their data
        user = User.query.get(session['user_id'])
        entries = DataEntry.query.filter_by(user_id=user.id).all()
        data = []
        for entry in entries:
            # Map item number to Persian name
            item_name = PERSIAN_ITEMS[int(entry.item) - 1]  # Subtract 1 because list is 0-indexed
            data.append({
                'Item Number': entry.item,
                'Item Name': item_name,  # Add Persian item name
                'Value': entry.value,
                'Document': entry.document_path if entry.document_path else 'No Document'
            })
        
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{user.full_name}_data.xlsx'
        )

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/create_user', methods=['GET', 'POST'])
def create_user():
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']
        phone = request.form['phone']

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('create_user'))

        new_user = User(username=username, password=password, email=email, full_name=full_name, phone=phone)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_user.html')

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.password = request.form['password']
        user.email = request.form['email']
        user.full_name = request.form['full_name']
        user.phone = request.form['phone']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_user.html', user=user)

@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_comment/<int:user_id>', methods=['GET', 'POST'])
def admin_add_comment(user_id):
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        content = request.form['admin_comment']
        new_comment = Comment(user_id=user.id, admin_comment=content, is_admin_comment=True)  # Admin comment
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('view_user', user_id=user.id))
    
    return render_template('admin_add_comment.html', user=user)

@app.route('/user/add_comment', methods=['GET', 'POST'])
def user_add_comment():
    if 'user_id' not in session or session['user_id'] == 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        content = request.form['content']
        new_comment = Comment(user_id=user.id, admin_comment=content, is_admin_comment=False)  # User comment
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('user_add_comment.html')


@app.route('/user/respond_comment/<int:comment_id>', methods=['GET', 'POST'])
def respond_comment(comment_id):
    if 'user_id' not in session or session['user_id'] == 'admin':
        return redirect(url_for('login'))
    
    comment = Comment.query.get(comment_id)
    
    if request.method == 'POST':
        response = request.form['user_response']
        comment.user_response = response
        db.session.commit()
        flash('Response submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('respond_comment.html', comment=comment)

@app.route('/admin/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    comment = Comment.query.get(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('view_user', user_id=comment.user_id))

@app.route('/admin/edit_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    comment = Comment.query.get(comment_id)
    
    if request.method == 'POST':
        comment.admin_comment = request.form['content']
        db.session.commit()
        flash('Comment updated successfully!', 'success')
        return redirect(url_for('view_user', user_id=comment.user_id))
    
    return render_template('edit_comment.html', comment=comment)

@app.route('/admin/analysis')
def analysis():
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    users = User.query.all()
    analysis_data = []
    
    for user in users:
        entries = DataEntry.query.filter_by(user_id=user.id).all()
        total_items = len(PERSIAN_ITEMS)  # Total number of Persian items (150)
        entered_items = len(entries)
        percentage = (entered_items / total_items) * 100
        
        analysis_data.append({
            'User': user.full_name,
            'Entered Items': entered_items,
            'Percentage': f'{percentage:.2f}%'
        })
    
    return render_template('analysis.html', analysis_data=analysis_data)

@app.route('/admin/download_analysis')
def download_analysis():
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    users = User.query.all()
    analysis_data = []
    
    for user in users:
        entries = DataEntry.query.filter_by(user_id=user.id).all()
        total_items = len(PERSIAN_ITEMS)  # Total number of Persian items (150)
        entered_items = len(entries)
        percentage = (entered_items / total_items) * 100
        
        analysis_data.append({
            'User': user.full_name,
            'Entered Items': entered_items,
            'Percentage': f'{percentage:.2f}%'
        })
    
    df = pd.DataFrame(analysis_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analysis')
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='analysis_data.xlsx'
    )

@app.route('/admin/promote_user/<int:user_id>')
def promote_user(user_id):
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'{user.full_name} has been promoted to admin!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/view_user/<int:user_id>')
def view_user(user_id):
    if 'user_id' not in session or session['user_id'] != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    entries = DataEntry.query.filter_by(user_id=user.id).all()
    data_dict = {int(entry.item): entry for entry in entries}  # Convert item to int for lookup
    comments = Comment.query.filter_by(user_id=user.id).all()
    
    return render_template('view_user.html', user=user, data_dict=data_dict, comments=comments, persian_items=PERSIAN_ITEMS)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)