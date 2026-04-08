import streamlit as st
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_transformation
import numpy as np
import matplotlib.pyplot as plt

# إعدادات الصفحة
st.set_page_config(page_title="ODE Pro Solver", layout="wide")

st.title("🎯 ODE Pro Solver - النسخة المستقرة")
st.markdown("""
**اكتب المعادلة بطريقة رياضية بسيطة.** 
أمثلة: `y' = 2xy` | `y' + y = x^2` | `y' = (x^2 + y^2)/x`
""")

# تعريف المتغيرات
x = sp.Symbol('x')
y = sp.Function('y')(x) # تعريف y كدالة من x مباشرة

# إعداد محرك التحليل الذكي (المسؤول عن فهم 2xy كـ 2*x*y)
transformations = (standard_transformations + (implicit_multiplication_transformation,))

def solve_ode(user_input):
    try:
        # 1. معالجة أولية للنص
        text = user_input.replace(' ', '')
        text = text.replace('^', '**')
        
        # تحويل y' إلى صيغة يفهمها SymPy قبل التحليل
        # نستخدم صيغة diff(y, x) بدلاً من y.diff(x) لضمان استقرار parse_expr
        text = text.replace("y'", "diff(y, x)")
        text = text.replace("dy/dx", "diff(y, x)")
        
        if '=' not in text:
            return None, "خطأ: يجب وضع علامة '=' للفصل بين طرفي المعادلة"
            
        lhs_str, rhs_str = text.split('=')
        
        # 2. استخدام محرك SymPy لتحويل النصوص إلى معادلات رياضية
        # نمرر local_dict ليعرف المحرك أن y هي الدالة التي عرفناها
        local_dict = {'x': x, 'y': y}
        
        lhs = parse_expr(lhs_str, local_dict=local_dict, transformations=transformations)
        rhs = parse_expr(rhs_str, local_dict=local_dict, transformations=transformations)
        
        equation = sp.Eq(lhs, rhs)
        
        # 3. حل المعادلة
        solution = sp.dsolve(equation, y)
        
        # استخراج الحل
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
    c_val = st.number_input("قيمة الثابت C (للرسم)", value=1.0)
    x_start = st.number_input("بداية محور X", value=0.1)
    
    solve_btn = st.button("حل المعادلة الآن 🚀")

if solve_btn:
    with col2:
        st.subheader("📝 النتائج")
        eq, result = solve_ode(user_input)
        
        if eq is not None:
            st.markdown("**المعادلة الرياضية:**")
            st.latex(sp.latex(eq))
            
            st.success("تم إيجاد الحل بنجاح!")
            st.markdown("**الحل العام (General Solution):**")
            st.latex(sp.latex(result))
            
            # تحليل نوع المعادلة
            st.info("**تصنيف المعادلة:**")
            try:
                # استخراج الطرف الأيمن لتحليله
                rhs_expr = sp.solve(eq, sp.diff(y, x))[0]
                if rhs_expr.is_linear():
                    st.write("📌 Linear Equation (معادلة خطية)")
                elif "y(x)**" in str(rhs_expr) or any(isinstance(item, sp.Pow) for item in rhs_expr.args):
                    st.write("📌 Bernoulli / Non-Linear (برنولي أو غير خطية)")
                else:
                    st.write("📌 Separable / Homogeneous / Exact")
            except:
                st.write("📌 First Order ODE")

            # الرسم البياني
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
                ax.plot(x_range, y_range, color='blue', linewidth=2)
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"تعذر رسم الدالة: {e}")
        else:
            st.error(result)

# دليل الكتابة في الجانب
st.sidebar.markdown("""
### 📖 دليل الكتابة النهائي:
الآن يمكنك الكتابة بأريحية تامة:

✅ **طرق الكتابة المدعومة:**
- المشتقة: `y'` أو `dy/dx`
- الضرب الضمني: `2xy` أو `5y` أو `xy` (سيفهمها البرنامج تلقائياً)
- الأس: `^` (مثال: `x^2`)
- الدوال: `exp(x)`, `sin(x)`, `sqrt(x)`
- اليساوي: يجب وضع `=` 

**أمثلة مضمونة:**
1. `y' = 2xy`
2. `y' + y = x^2`
3. `y' = (x^2 + y^2)/x`
4. `y' + y = x*y^2`
""")
