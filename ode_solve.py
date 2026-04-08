import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re

# إعدادات الصفحة
st.set_page_config(page_title="ODE Pro Solver", layout="wide")

st.title("🎯 ODE Pro Solver - الحل النهائي والمضمون")
st.markdown("""
**اكتب المعادلة بطريقة رياضية بسيطة.** 
أمثلة: `y' = 2xy` | `y' + y = x^2` | `y' = (x^2 + y^2)/x`
""")

# تعريف المتغيرات الأساسية
x = sp.Symbol('x')
y = sp.Function('y')

def mathematical_translator(text):
    """
    هذه الدالة تحول الكتابة البشرية الرياضية إلى لغة يفهمها بايثون و SymPy
    """
    # 1. حذف المسافات
    text = text.replace(' ', '')
    
    # 2. تحويل المشتقة y' إلى صيغة SymPy
    text = text.replace("y'", "y(x).diff(x)")
    text = text.replace("dy/dx", "y(x).diff(x)")
    
    # 3. تحويل الأسس ^ إلى **
    text = text.replace('^', '**')
    
    # 4. حل مشكلة الضرب الضمني (السر هنا)
    # تحويل رقم يليه حرف أو قوس (مثلاً 2y -> 2*y)
    text = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', text)
    # تحويل حرف يليه حرف أو قوس (مثلاً xy -> x*y)
    # نستثني الكلمات المحجوزة مثل sin, cos, exp, log
    def multiply_fix(match):
        group = match.group(0)
        protected = ['sin', 'cos', 'exp', 'log', 'tan', 'sqrt']
        for word in protected:
            if word in group:
                return group
        return group[0] + '*' + group[1:]

    # البحث عن أي تتابع من الحروف وتحويله لضرب (مع استثناء الدوال)
    text = re.sub(r'([a-zA-Z])([a-zA-Z\(])', multiply_fix, text)
    
    # 5. تحويل أي y متبقية إلى y(x) لضمان أنها دالة
    # نبحث عن y التي لا يتبعها (x) أو .diff
    text = re.sub(r'y(?!\(x\)|.diff)', 'y(x)', text)
    
    return text

def solve_ode(user_input):
    try:
        # ترجمة المعادلة
        translated_text = mathematical_translator(user_input)
        
        if '=' not in translated_text:
            return None, "خطأ: يجب وضع علامة '=' للفصل بين طرفي المعادلة"
            
        lhs_str, rhs_str = translated_text.split('=')
        
        # قاموس الدوال للـ eval
        safe_dict = {
            'x': x, 'y': y, 
            'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos, 
            'sqrt': sp.sqrt, 'log': sp.log, 'tan': sp.tan, 'pi': sp.pi
        }
        
        # تحويل النصوص إلى رموز رياضية
        lhs = eval(lhs_str, {"__builtins__": None}, safe_dict)
        rhs = eval(rhs_str, {"__builtins__": None}, safe_dict)
        equation = sp.Eq(lhs, rhs)
        
        # حل المعادلة تفاضلياً
        solution = sp.dsolve(equation, y)
        
        # استخراج الطرف الأيمن من الحل
        res = solution[0].rhs if isinstance(solution, list) else solution.rhs
        return equation, res
    except Exception as e:
        return None, f"خطأ في صياغة المعادلة: {str(e)}"

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
            # عرض المعادلة الأصلية بـ LaTeX
            st.markdown("**المعادلة التي تم تحليلها:**")
            st.latex(sp.latex(eq))
            
            st.success("تم إيجاد الحل بنجاح!")
            st.markdown("**الحل العام (General Solution):**")
            st.latex(sp.latex(result))
            
            # تحليل الطريقة
            st.info("**طريقة الحل المستخدمة:**")
            try:
                # تحليل بسيط جداً لنوع المعادلة
                if "y(x)**" in user_input:
                    st.write("📌 Bernoulli / Non-Linear")
                elif sp.solve(eq, y(x).diff(x))[0].is_linear():
                    st.write("📌 Linear Equation")
                else:
                    st.write("📌 Separable / Homogeneous / Exact")
            except:
                st.write("📌 First Order ODE")

            # الرسم البياني
            st.subheader("🖼️ الرسم البياني")
            try:
                # استبدال الثوابت (C1, C2...) بقيمة c_val
                final_expr = result
                for symbol in result.free_symbols:
                    if symbol != x:
                        final_expr = final_expr.subs(symbol, c_val)
                
                # تحويل لـ numpy للرسم
                f_num = sp.lambdify(x, final_expr, 'numpy')
                x_range = np.linspace(x_start, x_start + 5, 100)
                y_range = f_num(x_range)
                
                fig, ax = plt.subplots()
                ax.plot(x_range, y_range, color='green', linewidth=2)
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"تعذر رسم هذه المعادلة: {e}")
        else:
            st.error(result)

# دليل الكتابة
st.sidebar.markdown("""
### 📖 دليل الكتابة (مهم جداً):
الآن البرنامج يفهم لغتك الرياضية:

✅ **طرق الكتابة الصحيحة:**
- المشتقة: اكتب `y'` أو `dy/dx`
- الضرب: يمكنك كتابة `2y` أو `xy` أو `2*x*y`
- الأس: اكتب `^` (مثل `x^2`)
- الدوال: `exp(x)`, `sin(x)`, `sqrt(x)`
- اليساوي: يجب وضع `=` 

**أمثلة للتجربة:**
1. `y' = x*y` (Separable)
2. `y' + y = x^2` (Linear)
3. `y' = (x^2 + y^2)/x` (Homogeneous)
4. `y' + y = x*y^2` (Bernoulli)
""")
