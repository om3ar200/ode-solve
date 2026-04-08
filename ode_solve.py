import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# استيراد المحلل الذكي بشكل مباشر وصريح بدون try/except لتجنب الـ NameError
from sympy.parsing.sympy_parser import (
    parse_expr, 
    standard_transformations, 
    implicit_multiplication_transformation
)

# إعدادات الصفحة
st.set_page_config(page_title="ODE Pro Solver", layout="wide")

st.title("🎯 ODE Pro Solver - النسخة المستقرة والنهائية")
st.markdown("""
**اكتب المعادلة بطريقة رياضية بسيطة.** 
أمثلة: `y' = 2xy` | `y' + y = x^2` | `y' = (x^2 + y^2)/x`
""")

# تعريف المتغيرات
x = sp.Symbol('x')
y = sp.Function('y') # تعريف y كدالة (Symbolic Function)

# إعداد محرك التحليل الذكي (هذا السطر لن يسبب خطأ الآن لأن الاستيراد مباشر)
transformations = standard_transformations + (implicit_multiplication_transformation,)

def solve_ode(user_input):
    try:
        # 1. تنظيف النص
        text = user_input.replace(' ', '').replace('^', '**')
        
        # تحويل y' أو dy/dx إلى صيغة يفهمها parse_expr
        # نستخدم diff(y(x), x) لضمان الدقة
        text = text.replace("y'", "diff(y(x), x)").replace("dy/dx", "diff(y(x), x)")
        
        if '=' not in text:
            return None, "خطأ: يجب وضع علامة '=' للفصل بين طرفي المعادلة"
            
        lhs_str, rhs_str = text.split('=')
        
        # تعريف القاموس المحلي ليفهم المحرك أن y هي دالة و x هو رمز
        # لاحظ هنا أننا نمرر y كدالة
        local_dict = {'x': x, 'y': y}
        
        # 2. تحويل النصوص إلى معادلات رياضية باستخدام المحلل الذكي
        lhs = parse_expr(lhs_str, local_dict=local_dict, transformations=transformations)
        rhs = parse_expr(rhs_str, local_dict=local_dict, transformations=transformations)
        
        equation = sp.Eq(lhs, rhs)
        
        # 3. حل المعادلة التفاضلية
        # dsolve تحتاج أن تعرف أننا نحل بالنسبة للدالة y(x)
        solution = sp.dsolve(equation, y)
        
        # استخراج الحل (الطرف الأيمن)
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
            # عرض المعادلة الأصلية بتنسيق LaTeX
            st.markdown("**المعادلة التي تم تحليلها:**")
            st.latex(sp.latex(eq))
            
            st.success("تم إيجاد الحل بنجاح!")
            st.markdown("**الحل العام (General Solution):**")
            st.latex(sp.latex(result))
            
            # الرسم البياني
            st.subheader("🖼️ الرسم البياني")
            try:
                # استبدال الثوابت (مثل C1) بالقيمة المدخلة
                final_expr = result
                for symbol in result.free_symbols:
                    if symbol != x:
                        final_expr = final_expr.subs(symbol, c_val)
                
                # تحويل التعبير الرياضي إلى دالة numpy للرسم
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

st.sidebar.markdown("""
### 📖 دليل الكتابة:
- المشتقة: `y'` أو `dy/dx`
- الضرب الضمني: `2xy` (يعمل تلقائياً)
- الأس: `^` (مثال: `x^2`)
- الدوال: `exp(x)`, `sin(x)`, `sqrt(x)`
- اليساوي: يجب وضع `=` 

**أمثلة مضمونة:**
1. `y' = 2xy`
2. `y' + y = x^2`
3. `y' = (x^2 + y^2)/x`
""")
