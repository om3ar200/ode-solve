import streamlit as st
from sympy import symbols, Function, Eq, dsolve, latex, sympify, checkodesol
import matplotlib.pyplot as plt
import numpy as np

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Differential Equation Solver", layout="centered")

st.title("🧪 المحلل الذكي للمعادلات التفاضلية")
st.markdown("""
هذا الموقع يحل معادلات الدرجة الأولى (First Order ODEs) ويعرض لك **طريقة الحل** المتبعة والرسم البياني.
""")

# --- تعريف الرموز ---
x = symbols('x')
y = Function('y')(x)

# --- واجهة الإدخال ---
with st.expander("📝 تعليمات الكتابة (اقرأني)", expanded=False):
    st.write("""
    * للمشتقة $y'$ اكتب: `y(x).diff(x)`
    * للضرب استخدم `*` وللأس استخدم `**`
    * مثال لمعادلة Bernoulli: `y(x).diff(x) + y(x)/x - y(x)**2`
    """)

eqn_input = st.text_input("أدخل الطرف الأيسر للمعادلة (بفرض أنها تساوي 0):", "y(x).diff(x) + (1/x)*y(x) - x**2")

if st.button("حل المعادلة وإظهار الخطوات"):
    try:
        # 1. تحويل النص إلى كائن رياضي
        lhs = sympify(eqn_input)
        eqn = Eq(lhs, 0)

        # 2. عرض المعادلة بشكل رياضي
        st.subheader("1. المعادلة الرياضية:")
        st.latex(latex(eqn))

        # 3. تحديد نوع المعادلة (Classification)
        # هذه الدالة ترجع قائمة بكل الطرق التي يمكن حل المعادلة بها
        methods = dsolve(eqn, y, hint='all_rules')
        
        st.subheader("2. طرق الحل الممكنة:")
        if methods:
            # تنظيف أسماء الطرق لعرضها بشكل أفضل
            clean_methods = [m.replace('_', ' ').capitalize() for m in methods.keys() if 'internal' not in m]
            st.success(f"المعادلة يمكن حلها بطرق: {', '.join(clean_methods[:3])}")
        
        # 4. إيجاد الحل النهائي
        solution = dsolve(eqn, y)
        
        st.subheader("3. الحل العام:")
        st.latex(latex(solution))

        # 5. الرسم البياني (Solution Curve)
        st.subheader("4. التمثيل البياني (لـ C1 = 1):")
        try:
            # استخراج الطرف الأيمن من الحل وتعويض الثابت بقيمة 1 للرسم
            sol_expr = solution.rhs.subs('C1', 1)
            
            # تحويل المعادلة لدالة يمكن رسمها برمجياً
            f_plot = lambda val: float(sol_expr.subs(x, val))
            x_vals = np.linspace(0.1, 10, 100) # تجنب الصفر في حالة القسمة
            y_vals = [f_plot(v) for v in x_vals]

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label="y(x) at C1=1", color='blue')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)
        except:
            st.warning("تعذر رسم المنحنى لهذه المعادلة تحديداً، قد تكون النتيجة مركبة أو غير قابلة للتمثيل البسيط.")

    except Exception as e:
        st.error(f"خطأ في الصيغة: {e}")
        st.info("تأكد من كتابة y(x) دائماً وليس y فقط.")

# --- التذييل ---
st.markdown("---")
st.caption("تم التطوير بواسطة Coding Partner - يعمل بمحرك SymPy الرياضي.")