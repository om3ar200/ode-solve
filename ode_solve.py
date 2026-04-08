import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# إعدادات الصفحة
st.set_page_config(page_title="Math ODE Solver", layout="wide")

st.title("🎓 Mathematical ODE Solver")
st.markdown("""
أهلاً بك! الآن يمكنك كتابة المعادلات بطريقة رياضية بسيطة.
**أمثلة على طريقة الكتابة:**
- `y' = x * y`
- `y' + y = exp(x)`
- `y' = (x^2 + y^2) / x`
""")

# تعريف المتغيرات الرمزية
x = sp.Symbol('x')
y = sp.Function('y')(x)

def smart_parse(text):
    """
    تحويل الكتابة الرياضية البشرية إلى صيغة SymPy
    """
    # 1. تنظيف النص
    text = text.replace(' ', '')
    
    # 2. تحويل y' أو dy/dx إلى الصيغة البرمجية
    text = re.sub(r"y'", "y(x).diff(x)", text)
    text = re.sub(r"dy/dx", "y(x).diff(x)", text)
    
    # 3. تحويل الأسس من ^ إلى **
    text = text.replace('^', '**')
    
    # 4. التعامل مع y كدالة y(x) بدلاً من رمز بسيط
    # نبحث عن y متبوعة بأس أو عملية حسابية ونحولها لـ y(x)
    text = re.sub(r"y(?![ (])", "y(x)", text)
    
    # 5. تحويل علامة = إلى Eq()
    if '=' in text:
        lhs, rhs = text.split('=')
        # إنشاء قاموس للتقييم لضمان التعرف على الدوال
        safe_dict = {'x': x, 'y': y, 'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos, 'sqrt': sp.sqrt, 'log': sp.log, 'pi': sp.pi}
        try:
            return sp.Eq(eval(lhs, {"__builtins__": None}, safe_dict), 
                         eval(rhs, {"__builtins__": None}, safe_dict))
        except Exception as e:
            raise ValueError(f"خطأ في صياغة الطرفين: {e}")
    else:
        raise ValueError("يجب أن تحتوي المعادلة على علامة '='")

def solve_ode(user_input):
    try:
        # تحويل المدخلات "البشرية" إلى معادلة SymPy
        equation = smart_parse(user_input)
        
        # حل المعادلة
        solution = sp.dsolve(equation, y)
        
        # استخراج الحل
        res = solution[0].rhs if isinstance(solution, list) else solution.rhs
        return equation, res
    except Exception as e:
        return None, str(e)

# واجهة المستخدم
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("✍️ اكتب المعادلة رياضياً")
    user_input = st.text_input("مثال: y' = (x^2 + y^2)/x", value="y' = (x^2 + y^2)/x")
    
    st.subheader("⚙️ إعدادات الرسم")
    x_val = st.number_input("بداية محور x", value=1.0)
    c_val = st.number_input("قيمة الثابت C", value=1.0)
    
    solve_btn = st.button("حل المعادلة 🚀")

if solve_btn:
    with col2:
        st.subheader("📝 النتائج")
        eq, result = solve_ode(user_input)
        
        if eq is not None:
            # عرض المعادلة المدخلة بشكل رياضي
            st.markdown("**المعادلة التي أدخلتها:**")
            st.latex(sp.latex(eq))
            
            st.success("تم الحل بنجاح!")
            st.markdown("**الحل العام (General Solution):**")
            st.latex(sp.latex(result))
            
            # تحديد الطريقة
            st.info("**طريقة الحل المقترحة:**")
            try:
                # تحليل مبسط لنوع المعادلة
                rhs = sp.solve(eq, y.diff(x))[0]
                if rhs.is_linear():
                    st.write("- Linear (معادلة خطية)")
                elif "y(x)**" in user_input:
                    st.write("- Bernoulli / Non-Linear (برنولي أو غير خطية)")
                else:
                    st.write("- Separable / Exact (قابلة للفصل أو تامة)")
            except:
                st.write("- General ODE Method")

            # الرسم البياني
            st.subheader("🖼️ التمثيل البياني")
            try:
                # استبدال الثوابت
                final_expr = result
                for symbol in result.free_symbols:
                    if symbol != x:
                        final_expr = final_expr.subs(symbol, c_val)
                
                f_num = sp.lambdify(x, final_expr, 'numpy')
                x_range = np.linspace(x_val, x_val + 5, 100)
                y_range = f_num(x_range)
                
                fig, ax = plt.subplots()
                ax.plot(x_range, y_range, color='red', linewidth=2)
                ax.set_xlabel('x')
                ax.set_ylabel('y(x)')
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"لم يتمكن البرنامج من رسم الدالة: {e}")
        else:
            st.error(f"❌ خطأ: {result}")

# شريط جانبي للإرشادات
st.sidebar.markdown("""
### 📖 كيف تكتب المعادلات؟
بدلاً من كتابة أكواد، اكتب كما تكتب في ورقتك:

- **المشتقة**: اكتب `y'` أو `dy/dx`
- **يساوي**: اكتب `=`
- **الأس**: اكتب `^` (مثلاً `y^2`)
- **الدوال**: `exp(x)`, `sin(x)`, `sqrt(x)`

**أمثلة سريعة:**
1. `y' = x*y`
2. `y' + y = exp(x)`
3. `y' = (x^2 + y^2)/x`
4. `y' = 1/(x+y)`
""")
