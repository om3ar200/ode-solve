import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# إعدادات الصفحة
st.set_page_config(page_title="ODE Solver Pro", layout="wide")

st.title("🧮 First-Order ODE Solver")
st.markdown("""
هذا الموقع يقوم بتحليل وحل المعادلات التفاضلية من الرتبة الأولى. 
يرجى كتابة المعادلة كما هو موضح في الدليل على اليسار.
""")

# تعريف المتغيرات الرمزية بشكل صحيح
x = sp.Symbol('x')
y = sp.Function('y') # تعريف y كدالة وليس كقيمة

# قاموس الدوال المسموح بها في eval لضمان عمل Eq و sin و cos وغيرها
safe_dict = {
    'Eq': sp.Eq,
    'sp': sp,
    'x': x,
    'y': y,
    'sin': sp.sin,
    'cos': sp.cos,
    'exp': sp.exp,
    'sqrt': sp.sqrt,
    'log': sp.log,
    'tan': sp.tan,
    'pi': sp.pi
}

def solve_ode(eq_str):
    try:
        # استخدام safe_dict لكي يتعرف البرنامج على Eq و y(x)
        # يتم تمرير القاموس لـ eval لتعريف الرموز
        equation = eval(eq_str, {"__builtins__": None}, safe_dict)
        
        # حل المعادلة باستخدام dsolve
        solution = sp.dsolve(equation, y)
        
        # استخراج الناتج (الطرف الأيمن من المعادلة)
        if isinstance(solution, list):
            res = solution[0].rhs
        else:
            res = solution.rhs
            
        return equation, res
    except Exception as e:
        return None, str(e)

# تقسيم الشاشة
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 إدخال المعادلة")
    user_input = st.text_input("أدخل المعادلة هنا:", value="Eq(y(x).diff(x), (x**2 + y(x)**2)/x)")
    
    st.subheader("📉 إعدادات الرسم البياني")
    x_start = st.number_input("قيمة x الابتدائية", value=1.0)
    c_val = st.number_input("قيمة الثابت C", value=1.0)
    
    solve_btn = st.button("حل المعادلة الآن 🚀")

if solve_btn:
    with col2:
        st.subheader("📝 الحل والتحليل")
        
        eq, result = solve_ode(user_input)
        
        if eq is not None:
            # عرض المعادلة الأصلية بـ LaTeX
            st.latex(f"$$\text{{Equation: }} {sp.latex(eq)}$$")
            
            st.success("تم إيجاد الحل بنجاح!")
            # عرض الحل النهائي بـ LaTeX
            st.latex(f"$$\text{{General Solution: }} {sp.latex(result)}$$")
            
            # محاولة تحديد نوع المعادلة (تبسيط)
            st.info("**تحليل طريقة الحل:**")
            try:
                rhs = sp.solve(eq, y(x).diff(x))[0]
                methods = []
                if rhs.is_linear(): methods.append("Linear")
                if "y(x)**" in user_input: methods.append("Bernoulli / Non-Linear")
                # اختبار بسيط للفصل
                if sp.simplify(rhs/rhs.subs(y(x), 1)) == 1: methods.append("Separable")
                
                if not methods: methods.append("Exact / Substitution")
                
                for m in methods:
                    st.write(f"- {m}")
            except:
                st.write("- معادلة عامة (General Method)")

            # --- الرسم البياني ---
            st.subheader("🖼️ الرسم البياني")
            try:
                # استبدال الثوابت (مثل C1) بالقيمة التي أدخلها المستخدم
                final_expr = result
                for symbol in result.free_symbols:
                    if symbol != x:
                        final_expr = final_expr.subs(symbol, c_val)
                
                # تحويل التعبير الرياضي إلى دالة numpy
                f_num = sp.lambdify(x, final_expr, 'numpy')
                
                x_range = np.linspace(x_start, x_start + 5, 100)
                y_range = f_num(x_range)
                
                fig, ax = plt.subplots()
                ax.plot(x_range, y_range, label=f'C = {c_val}', color='blue', linewidth=2)
                ax.set_xlabel('x')
                ax.set_ylabel('y(x)')
                ax.set_title('Solution Curve')
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"لا يمكن رسم هذه الدالة حالياً: {e}")
        else:
            st.error(f"خطأ في صياغة المعادلة: {result}")

# دليل الكتابة في الشريط الجانبي
st.sidebar.markdown("""
### 💡 دليل الكتابة الصحيح:
يجب كتابة المعادلة بدقة لكي يفهمها البرنامج:

1. **المشتقة $y'$**: تكتب `y(x).diff(x)`
2. **علامة اليساوي**: نستخدم `Eq( الطرف الأول, الطرف الثاني )`
3. **الأس**: $x^2$ يكتب `x**2`
4. **الجذر**: $\sqrt{x}$ يكتب `sqrt(x)`
5. **الدوال**: `sin(x)`, `cos(x)`, `exp(x)`

---
### 📋 أمثلة جاهزة (انسخها):

**1. Separable:**
`Eq(y(x).diff(x), x*y(x))`

**2. Linear:**
`Eq(y(x).diff(x) + y(x), exp(x))`

**3. Bernoulli:**
`Eq(y(x).diff(x) + y(x), x*y(x)**2)`

**4. Homogeneous:**
`Eq(y(x).diff(x), (x**2 + y(x)**2)/x)`
""")
