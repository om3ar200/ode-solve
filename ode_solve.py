import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# إعدادات الصفحة
st.set_page_config(page_title="ODE Master Solver", layout="wide")

st.title("🎓 ODE Master Solver - حل المعادلات التفاضلية")
st.markdown("""
هذا الإصدار يدعم الكتابة الرياضية الطبيعية. 
**أمثلة مدعومة:** `y' = 2xy`, `y' + y = x^2`, `y' = (x^2 + y^2)/x`
""")

# تعريف المتغيرات
x = sp.Symbol('x')
y = sp.Function('y')

def preprocess_math(text):
    """
    تنظيف النص وتحويل الكتابة البشرية إلى صيغة يفهمها SymPy
    """
    text = text.replace(' ', '')
    
    # 1. تحويل المشتقة
    text = re.sub(r"y'", "y(x).diff(x)", text)
    text = re.sub(r"dy/dx", "y(x).diff(x)", text)
    
    # 2. تحويل الأسس
    text = text.replace('^', '**')
    
    # 3. معالجة الضرب الضمني (أهم خطوة)
    # تحويل (رقم)(حرف) مثل 2y -> 2*y
    text = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', text)
    # تحويل (حرف)(حرف) مثل xy -> x*y
    text = re.sub(r'([a-zA-Z])([a-zA-Z\(])', r'\1*\2', text)
    # استثناء: لا نريد تحويل sin, cos, exp إلى s*i*n
    # سنقوم بإعادة تصحيح الدوال المشهورة
    for func in ['sin', 'cos', 'exp', 'log', 'tan', 'sqrt']:
        text = text.replace(f'{func[0]}*{func[1:]}', func)

    # 4. تحويل y إلى y(x) في كل مكان ليس مشتقة
    text = re.sub(r"y(?!\(x\).diff)", "y(x)", text)
    
    return text

def solve_ode(user_input):
    try:
        # معالجة النص
        processed_text = preprocess_math(user_input)
        
        if '=' not in processed_text:
            return None, "يجب وجود علامة '=' في المعادلة"
            
        lhs_str, rhs_str = processed_text.split('=')
        
        # قاموس الدوال
        safe_dict = {
            'x': x, 'y': y, 
            'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos, 
            'sqrt': sp.sqrt, 'log': sp.log, 'tan': sp.tan, 'pi': sp.pi
        }
        
        # تحويل النصوص إلى تعبيرات SymPy
        lhs = eval(lhs_str, {"__builtins__": None}, safe_dict)
        rhs = eval(rhs_str, {"__builtins__": None}, safe_dict)
        equation = sp.Eq(lhs, rhs)
        
        # حل المعادلة
        solution = sp.dsolve(equation, y)
        
        # استخراج الحل النهائي
        res = solution[0].rhs if isinstance(solution, list) else solution.rhs
        return equation, res
    except Exception as e:
        return None, f"خطأ في تحليل المعادلة: {str(e)}"

# واجهة المستخدم
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("✍️ أدخل المعادلة")
    user_input = st.text_input("اكتب المعادلة هنا:", value="y' = x*y")
    
    st.subheader("📉 إعدادات الرسم")
    x_start = st.number_input("بداية محور X", value=0.1)
    c_val = st.number_input("قيمة الثابت C", value=1.0)
    
    solve_btn = st.button("احسب الحل الآن 🚀")

if solve_btn:
    with col2:
        st.subheader("📝 النتائج")
        eq, result = solve_ode(user_input)
        
        if eq is not None:
            st.markdown("**المعادلة الرياضية:**")
            st.latex(sp.latex(eq))
            
            st.success("تم إيجاد الحل!")
            st.markdown("**الحل العام:**")
            st.latex(sp.latex(result))
            
            # تحليل النوع
            st.info("**تصنيف المعادلة:**")
            try:
                # محاولة بسيطة لتحديد النوع
                if "y(x)**" in user_input:
                    st.write("📌 Bernoulli / Non-Linear")
                elif sp.solve(eq, y(x).diff(x))[0].is_linear():
                    st.write("📌 Linear")
                else:
                    st.write("📌 Separable / Exact / Homogeneous")
            except:
                st.write("📌 First Order ODE")

            # الرسم البياني
            st.subheader("🖼️ الرسم البياني")
            try:
                final_expr = result
                # استبدال أي ثابت C1, C2 بقيمة c_val
                for symbol in result.free_symbols:
                    if symbol != x:
                        final_expr = final_expr.subs(symbol, c_val)
                
                f_num = sp.lambdify(x, final_expr, 'numpy')
                x_range = np.linspace(x_start, x_start + 5, 100)
                y_range = f_num(x_range)
                
                fig, ax = plt.subplots()
                ax.plot(x_range, y_range, color='blue', linewidth=2)
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"تعذر الرسم: {e}")
        else:
            st.error(f"❌ {result}")

# دليل في الجانب
st.sidebar.markdown("""
### 📖 دليل الكتابة السريع:
الآن يمكنك الكتابة بشكل طبيعي جداً:

✅ **مسموح:**
- `y' = 2xy` (بدل `2*x*y`)
- `y' = x^2` (بدل `x**2`)
- `y' + y = exp(x)`
- `y' = (x^2 + y^2)/x`

❌ **تجنب:**
- كتابة حروف غير معروفة (مثل `q` أو `z`).
- نسيان علامة `=` .
""")
