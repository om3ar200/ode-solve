import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from sympy.integrals import integrate

# إعدادات الصفحة
st.set_page_config(page_title="ODE Solver Pro", layout="wide")

st.title("🧮 First-Order ODE Solver")
st.markdown("""
هذا الموقع يقوم بتحليل وحل المعادلات التفاضلية من الرتبة الأولى باستخدام عدة طرق. 
يرجى كتابة المعادلة بصيغة `y(x).diff(x)` لتمثيل $y'$.
مثال: `Eq(y(x).diff(x), (x**2 + y(x)**2)/x)`
""")

# تعريف المتغيرات الرمزية
x = sp.Symbol('x')
y = sp.Function('y')(x)

def detect_method(eq):
    """
    دالة لمحاولة اكتشاف طريقة الحل المناسبة
    """
    # تحويل المعادلة إلى صيغة y' = f(x, y)
    try:
        # نحاول جعل المعادلة على شكل y' = ...
        rhs = sp.solve(eq, y.diff(x))[0]
    except:
        return "Unknown", "المعادلة غير مكتوبة بصيغة صحيحة"

    # 1. التحقق من Linear (y' + P(x)y = Q(x))
    # المعادلة الخطية تكون خطية بالنسبة لـ y و y'
    if rhs.is_linear(): # تبسيط للتحقق
        # تحقق إضافي: هل تظهر y فقط كقوة 1؟
        # (هذا تبسيط، SymPy يقوم بالتحقق داخلياً)
        pass

    # 2. التحقق من Separable (f(x)g(y))
    # إذا كان من الممكن فصل x عن y في الطرف الأيمن
    # نختبر ذلك بقسمة f(x,y) على f(x,0) مثلاً أو البحث عن ضرب
    # هنا سنعتمد على SymPy dsolve في تحديد الطريقة ولكن سنصنفها يدوياً للتبسيط
    
    return "Analyzing...", rhs

def solve_ode(eq_str):
    try:
        # تحويل النص إلى تعبير رياضي من SymPy
        # نستخدم eval بحذر هنا، في الإنتاج يفضل استخدام parser
        equation = eval(eq_str)
        
        # حل المعادلة باستخدام dsolve
        # dsolve تحاول تجربة كل الطرق (Linear, Bernoulli, Separable, Exact)
        solution = sp.dsolve(equation, y)
        
        # استخراج الناتج
        res = solution[0].rhs if isinstance(solution, list) else solution.rhs
        return equation, res
    except Exception as e:
        return None, str(e)

# واجهة المستخدم
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 إدخال المعادلة")
    user_input = st.text_input("أدخل المعادلة هنا:", value="Eq(y(x).diff(x), (x**2 + y(x)**2)/x)")
    
    # إضافة خيار للقيم الابتدائية للرسم
    st.subheader("📉 إعدادات الرسم البياني")
    x_val = st.number_input("قيمة x الابتدائية", value=1.0)
    y_val = st.number_input("قيمة y الابتدائية (C)", value=1.0)
    
    solve_btn = st.button("حل المعادلة الآن 🚀")

if solve_btn:
    with col2:
        st.subheader("📝 الحل والتحليل")
        
        eq, result = solve_ode(user_input)
        
        if eq is not None:
            # عرض المعادلة المدخلة بـ LaTeX
            st.latex(f"$$\text{{Equation: }} {sp.latex(eq)}$$")
            
            # تحديد الطريقة (محاكاة للتحليل)
            # SymPy لا يخبرنا صراحة بالطريقة، لذا سنقوم بتحليل التعبير
            # سنقوم بعرض الحل النهائي بشكل جميل
            st.success("تم إيجاد الحل بنجاح!")
            st.latex(f"$$\text{{General Solution: }} {sp.latex(result)}$$")
            
            # محاولة تحديد الطريقة بناءً على شكل المعادلة
            # ملاحظة: هذا الجزء تقريبي لأن SymPy يدمج الطرق
            st.info("**طرق الحل الممكنة لهذه المعادلة:**")
            
            # منطق بسيط لتخمين الطريقة
            rhs = sp.solve(eq, y.diff(x))[0]
            methods = []
            if rhs.is_linear(): methods.append("Linear")
            if "y(x)**" in user_input: methods.append("Bernoulli or Non-Linear")
            if sp.simplify(rhs/rhs.subs(y, 1)) == 1: methods.append("Separable") # تبسيط
            if not methods: methods.append("Exact / Substitution")
            
            for m in methods:
                st.write(f"- {m}")

            # --- الجزء الخاص بالرسم البياني ---
            st.subheader("🖼️ الرسم البياني")
            try:
                # تحويل الحل الرمزي إلى دالة رقمية
                # استبدال الثابت C بالقيمة التي أدخلها المستخدم
                # عادة SymPy يضع الثابت كـ C1
                final_expr = result
                # البحث عن الثوابت واستبدالها
                for symbol in result.free_symbols:
                    if not symbol == x:
                        final_expr = final_expr.subs(symbol, y_val)
                
                f_num = sp.lambdify(x, final_expr, 'numpy')
                
                x_range = np.linspace(x_val, x_val + 5, 100)
                y_range = f_num(x_range)
                
                fig, ax = plt.subplots()
                ax.plot(x_range, y_range, label=f'C = {y_val}', color='blue', linewidth=2)
                ax.set_xlabel('x')
                ax.set_ylabel('y(x)')
                ax.set_title('Solution Curve')
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"تعذر رسم الدالة: {e}")
        else:
            st.error(f"خطأ في المعادلة: {result}")

# تعليمات للمستخدم
st.sidebar.markdown("""
### 💡 دليل الكتابة:
- لعمل مشتقة $y'$ اكتب: `y(x).diff(x)`
- لعمل يساوي اكتب: `Eq(الطرف الأول, الطرف الثاني)`
- الأس $x^2$ يكتب: `x**2`
- الجذر $\sqrt{x}$ يكتب: `sp.sqrt(x)`
- الدوال المثلثية: `sp.sin(x)`, `sp.cos(x)`

**أمثلة جاهزة:**
1. **Separable:** `Eq(y(x).diff(x), x*y(x))`
2. **Linear:** `Eq(y(x).diff(x) + y(x), sp.exp(x))`
3. **Bernoulli:** `Eq(y(x).diff(x) + y(x), x*y(x)**2)`
4. **Homogeneous:** `Eq(y(x).diff(x), (x**2 + y(x)**2)/x)`
""")
