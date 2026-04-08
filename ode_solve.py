import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
# استيراد المحلل الذكي بطريقة أكثر أماناً
try:
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_transformation
except ImportError:
    # في حال وجود إصدار قديم جداً
    from sympy import parse_expr

# إعدادات الصفحة
st.set_page_config(page_title="ODE Pro Solver", layout="wide")

st.title("🎯 ODE Pro Solver - النسخة النهائية")
st.markdown("""
**اكتب المعادلة بطريقة رياضية بسيطة.** 
أمثلة: `y' = 2xy` | `y' + y = x^2` | `y' = (x^2 + y^2)/x`
""")

# تعريف المتغيرات
x = sp.Symbol('x')
y = sp.Function('y')(x)

# إعداد محرك التحليل الذكي
transformations = (standard_transformations + (implicit_multiplication_transformation,))

def solve_ode(user_input):
    try:
        # تنظيف النص
        text = user_input.replace(' ', '').replace('^', '**')
        text = text.replace("y'", "diff(y, x)").replace("dy/dx", "diff(y, x)")
        
        if '=' not in text:
            return None, "خطأ: يجب وضع علامة '=' للفصل بين الطرفين"
            
        lhs_str, rhs_str = text.split('=')
        local_dict = {'x': x, 'y': y}
        
        # تحويل النصوص إلى معادلات باستخدام المحلل الذكي
        lhs = parse_expr(lhs_str, local_dict=local_dict, transformations=transformations)
        rhs = parse_expr(rhs_str, local_dict=local_dict, transformations=transformations)
        equation = sp.Eq(lhs, rhs)
        
        # حل المعادلة
        solution = sp.dsolve(equation, y)
        res = solution[0].rhs if isinstance(solution, list) else solution.rhs
        return equation, res
        
    except Exception as e:
        return None, f"خطأ في تحليل المعادلة: {str(e)}"

# الواجهة
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("✍️ إدخال المعادلة")
    user_input = st.text_input("اكتب هنا (مثال: y' = 2xy)", value="y' = 2xy")
    st.subheader("📉 إعدادات الرسم")
    c_val = st.number_input("قيمة الثابت C", value=1.0)
    x_start = st.number_input("بداية محور X", value=0.1)
    solve_btn = st.button("حل المعادلة الآن 🚀")

if solve_btn:
    with col2:
        st.subheader("📝 النتائج")
        eq, result = solve_ode(user_input)
        if eq is not None:
            st.latex(sp.latex(eq))
            st.success("تم الحل!")
            st.latex(sp.latex(result))
            
            # الرسم
            st.subheader("🖼️ الرسم البياني")
            try:
                final_expr = result
                for symbol in result.free_symbols:
                    if symbol != x:
                        final_expr = final_expr.subs(symbol, c_val)
                f_num = sp.lambdify(x, final_expr, 'numpy')
                x_range = np.linspace(x_start, x_start + 5, 100)
                y_range = f_num(x_range)
                fig, ax = plt.subplots()
                ax.plot(x_range, y_range, color='blue')
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"تعذر الرسم: {e}")
        else:
            st.error(result)

st.sidebar.markdown("""
### 📖 تنبيه هام جداً:
لكي يعمل الموقع على Streamlit Cloud، **يجب** وجود ملف باسم `requirements.txt` يحتوي على:
- `streamlit`
- `sympy`
- `numpy`
- `matplotlib`
""")
