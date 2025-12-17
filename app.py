"""
🏃‍♂️ MONITOR DE FATIGA Y RECUPERACIÓN - RUNNING
Aplicación web interactiva con Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Monitor de Fatiga - Running",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de visualización
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================
# FUNCIONES DE ANÁLISIS
# ============================================

def calcular_cargas(df, tss_col='TSS_Estimado'):
    """Calcula ATL, CTL y TSB usando promedios móviles exponenciales"""
    fecha_min = df['Fecha'].min()
    fecha_max = df['Fecha'].max()
    fecha_rango = pd.date_range(start=fecha_min, end=fecha_max, freq='D')
    
    df_completo = pd.DataFrame({'Fecha': fecha_rango})
    df_completo = df_completo.merge(df[['Fecha', tss_col]], on='Fecha', how='left')
    df_completo[tss_col] = df_completo[tss_col].fillna(0)
    
    df_completo['ATL'] = df_completo[tss_col].ewm(span=7, adjust=False).mean()
    df_completo['CTL'] = df_completo[tss_col].ewm(span=42, adjust=False).mean()
    df_completo['TSB'] = df_completo['CTL'] - df_completo['ATL']
    
    df_result = df.merge(df_completo[['Fecha', 'ATL', 'CTL', 'TSB']], on='Fecha', how='left')
    return df_result

def calcular_acwr(df):
    """Calcula el ratio Agudo:Crónico para detectar riesgo de lesión"""
    df['TSS_7d'] = df['TSS_Estimado'].rolling(window=7, min_periods=1).sum()
    df['TSS_28d'] = df['TSS_Estimado'].rolling(window=28, min_periods=1).sum()
    df['ACWR'] = df['TSS_7d'] / (df['TSS_28d'] / 4)
    
    def clasificar_riesgo(acwr):
        if pd.isna(acwr):
            return 'Sin datos'
        elif acwr < 0.8:
            return 'Subcarga'
        elif 0.8 <= acwr <= 1.3:
            return 'Zona Segura'
        elif 1.3 < acwr <= 1.5:
            return 'Precaución'
        else:
            return 'Alto Riesgo'
    
    df['Riesgo_Lesion'] = df['ACWR'].apply(clasificar_riesgo)
    return df

def calcular_eficiencia_cardiaca(df):
    """Calcula eficiencia cardíaca para detectar fatiga"""
    def ritmo_a_segundos(ritmo_str):
        try:
            if pd.isna(ritmo_str):
                return np.nan
            partes = str(ritmo_str).split(':')
            return int(partes[0]) * 60 + int(partes[1])
        except:
            return np.nan
    
    df['Ritmo_seg_km'] = df['Ritmo medio'].apply(ritmo_a_segundos)
    df['Velocidad_kmh'] = 3600 / df['Ritmo_seg_km']
    df['Eficiencia_Cardiaca'] = df['Frecuencia cardiaca media'] / df['Velocidad_kmh']
    df['Eficiencia_Baseline'] = df['Eficiencia_Cardiaca'].rolling(window=10, min_periods=3).mean()
    df['Desviacion_Eficiencia'] = ((df['Eficiencia_Cardiaca'] - df['Eficiencia_Baseline']) / 
                                    df['Eficiencia_Baseline'] * 100)
    return df

def clasificar_entreno(row):
    """Clasifica tipo de entrenamiento según día de la semana"""
    dia = row['Dia_Numero']
    if dia == 1:  # Martes
        return 'Ritmo Sostenido'
    elif dia == 3:  # Jueves
        return 'Series/Intervalos'
    elif dia == 5:  # Sábado
        return 'Fondo'
    else:
        return 'Otro'

def procesar_datos(df):
    """Procesa el DataFrame con todos los cálculos necesarios"""
    # Preparar datos básicos
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df = df.sort_values('Fecha').reset_index(drop=True)
    
    # Usar TE aeróbico como aproximación de TSS
    df['TE aeróbico'] = pd.to_numeric(df['TE aeróbico'], errors='coerce')
    df['TSS_Estimado'] = df['TE aeróbico'] * 20
    
    # Clasificar días de entrenamiento
    df['Dia_Semana'] = df['Fecha'].dt.day_name()
    df['Dia_Numero'] = df['Fecha'].dt.dayofweek
    df['Tipo_Entreno'] = df.apply(clasificar_entreno, axis=1)
    
    # Calcular métricas
    df = calcular_cargas(df)
    df = calcular_acwr(df)
    df = calcular_eficiencia_cardiaca(df)
    
    return df
# ============================================
# INTERFAZ PRINCIPAL
# ============================================

# Título
st.title("🏃‍♂️ Monitor de Fatiga y Recuperación")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📁 Cargar Datos")
    uploaded_file = st.file_uploader(
        "Subí tu CSV de entrenamientos",
        type=['csv'],
        help="Archivo CSV exportado desde Garmin/Strava con tus datos de running"
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ Instrucciones")
    st.markdown("""
    1. Exportá tus datos desde Garmin Connect o Strava
    2. Subí el archivo CSV
    3. ¡Visualizá tu análisis de fatiga!
    
    **Actualización:** Subí el CSV actualizado cada semana para ver tu progreso.
    """)

# ============================================
# PROCESAMIENTO Y ANÁLISIS
# ============================================

if uploaded_file is not None:
    try:
        # Cargar datos
        df = pd.read_csv(uploaded_file)
        
        # Procesar datos
        with st.spinner('Procesando datos...'):
            df = procesar_datos(df)
        
        st.success(f"✅ Datos cargados correctamente: {len(df)} entrenamientos")
        
        # Información básica
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Entrenamientos", len(df))
        with col2:
            st.metric("📅 Rango", f"{(df['Fecha'].max() - df['Fecha'].min()).days} días")
        with col3:
            st.metric("🏃 Distancia Total", f"{df['Distancia'].sum():.1f} km")
        with col4:
            st.metric("⚡ TE Promedio", f"{df['TE aeróbico'].mean():.2f}")
        
        st.markdown("---")
        
        # ============================================
        # PANEL DE ALERTAS
        # ============================================
        
        st.header("🚨 Panel de Alertas - Estado Actual")
        
        ultimo = df.iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        
        # Alerta 1: TSB (Frescura)
        with col1:
            st.subheader("🎯 Nivel de Frescura (TSB)")
            tsb = ultimo['TSB']
            
            if tsb > 5:
                st.success(f"**FRESCO** ({tsb:.1f})")
                st.write("✅ Estás en forma óptima")
            elif tsb > -5:
                st.info(f"**EQUILIBRADO** ({tsb:.1f})")
                st.write("⚖️ Balance perfecto")
            elif tsb > -10:
                st.warning(f"**MODERADAMENTE FATIGADO** ({tsb:.1f})")
                st.write("⚠️ Considerá recuperación")
            else:
                st.error(f"**MUY FATIGADO** ({tsb:.1f})")
                st.write("🚨 Necesitás recuperación urgente")
        
        # Alerta 2: ACWR (Riesgo de lesión)
        with col2:
            st.subheader("⚠️ Riesgo de Lesión (ACWR)")
            acwr = ultimo['ACWR']
            riesgo = ultimo['Riesgo_Lesion']
            
            if riesgo == 'Zona Segura':
                st.success(f"**BAJO** ({acwr:.2f})")
                st.write("✅ Carga óptima")
            elif riesgo == 'Precaución':
                st.warning(f"**MODERADO** ({acwr:.2f})")
                st.write("⚠️ No aumentes volumen")
            elif riesgo == 'Alto Riesgo':
                st.error(f"**ALTO** ({acwr:.2f})")
                st.write("🚨 Reducí volumen ya")
            else:
                st.info(f"**{riesgo}** ({acwr:.2f})")
        
        # Alerta 3: Eficiencia Cardíaca
        with col3:
            st.subheader("💓 Eficiencia Cardíaca")
            if not pd.isna(ultimo['Desviacion_Eficiencia']):
                desv = ultimo['Desviacion_Eficiencia']
                
                if desv < 5:
                    st.success(f"**NORMAL** ({desv:+.1f}%)")
                    st.write("✅ Corazón responde bien")
                elif desv < 10:
                    st.warning(f"**LIGERAMENTE ELEVADA** ({desv:+.1f}%)")
                    st.write("⚠️ Posible fatiga leve")
                else:
                    st.error(f"**DETERIORADA** ({desv:+.1f}%)")
                    st.write("🚨 Señal de fatiga")
            else:
                st.info("Sin datos suficientes")
        
        st.markdown("---")
        
        # ============================================
        # DETALLES DEL ÚLTIMO ENTRENAMIENTO
        # ============================================
        
        st.header("📋 Último Entrenamiento")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📅 Fecha", ultimo['Fecha'].strftime('%d/%m/%Y'))
        with col2:
            st.metric("🏃 Tipo", ultimo['Tipo_Entreno'])
        with col3:
            st.metric("📏 Distancia", f"{ultimo['Distancia']:.2f} km")
        with col4:
            st.metric("⚡ TSS Estimado", f"{ultimo['TSS_Estimado']:.1f}")
        with col5:
            st.metric("💪 TE aeróbico", f"{ultimo['TE aeróbico']:.1f}")
        
        st.markdown("---")
        # ============================================
        # GRÁFICOS
        # ============================================
        
        st.header("📊 Visualizaciones")
        
        # Tabs para organizar gráficos
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Fatiga & Fitness", "⚠️ Riesgo de Lesión", "💓 Eficiencia", "📊 Por Tipo"])
        
        with tab1:
            st.subheader("Fatiga (ATL) vs Fitness (CTL) y TSB")
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Gráfico 1: ATL y CTL
            ax1.plot(df['Fecha'], df['ATL'], label='ATL (Fatiga)', linewidth=2, color='red')
            ax1.plot(df['Fecha'], df['CTL'], label='CTL (Fitness)', linewidth=2, color='blue')
            ax1.fill_between(df['Fecha'], 0, df['ATL'], alpha=0.2, color='red')
            ax1.fill_between(df['Fecha'], 0, df['CTL'], alpha=0.2, color='blue')
            ax1.set_title('Fatiga (ATL) vs Fitness (CTL)', fontweight='bold')
            ax1.set_ylabel('Carga de Entrenamiento')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Gráfico 2: TSB
            colors = ['green' if x > 0 else 'red' for x in df['TSB']]
            ax2.bar(df['Fecha'], df['TSB'], color=colors, alpha=0.6)
            ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
            ax2.axhline(y=-10, color='orange', linestyle='--', linewidth=1, label='Zona de fatiga')
            ax2.set_title('TSB (Form/Frescura)', fontweight='bold')
            ax2.set_xlabel('Fecha')
            ax2.set_ylabel('TSB')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with tab2:
            st.subheader("Ratio Agudo:Crónico (ACWR)")
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(df['Fecha'], df['ACWR'], marker='o', linewidth=2, markersize=6)
            ax.axhspan(0.8, 1.3, alpha=0.2, color='green', label='Zona Segura')
            ax.axhspan(1.3, 1.5, alpha=0.2, color='orange', label='Precaución')
            if df['ACWR'].max() > 1.5:
                ax.axhspan(1.5, df['ACWR'].max() * 1.1, alpha=0.2, color='red', label='Alto Riesgo')
            ax.set_title('Ratio Agudo:Crónico (ACWR)', fontweight='bold', fontsize=14)
            ax.set_xlabel('Fecha')
            ax.set_ylabel('ACWR')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Distribución de riesgo
            st.subheader("Distribución de Riesgo de Lesión")
            riesgo_counts = df['Riesgo_Lesion'].value_counts()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            colores_riesgo = {'Zona Segura': 'green', 'Precaución': 'orange', 
                              'Alto Riesgo': 'red', 'Subcarga': 'lightblue', 'Sin datos': 'gray'}
            colors_pie = [colores_riesgo.get(x, 'gray') for x in riesgo_counts.index]
            ax.pie(riesgo_counts.values, labels=riesgo_counts.index, autopct='%1.1f%%',
                   colors=colors_pie, startangle=90)
            ax.set_title('Distribución de Riesgo de Lesión', fontweight='bold')
            
            st.pyplot(fig)
        
        with tab3:
            st.subheader("Eficiencia Cardíaca")
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(df['Fecha'], df['Eficiencia_Cardiaca'], marker='o', label='Eficiencia Real', linewidth=2)
            ax.plot(df['Fecha'], df['Eficiencia_Baseline'], label='Baseline', linewidth=2, linestyle='--', color='green')
            ax.set_title('Eficiencia Cardíaca (menor es mejor)', fontweight='bold', fontsize=14)
            ax.set_xlabel('Fecha')
            ax.set_ylabel('FC / Velocidad')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with tab4:
            st.subheader("TSS Estimado por Tipo de Entrenamiento")
            
            fig, ax = plt.subplots(figsize=(12, 6))
            colores_tipo = {'Ritmo Sostenido': 'orange', 'Series/Intervalos': 'red', 'Fondo': 'blue', 'Otro': 'gray'}
            for tipo in df['Tipo_Entreno'].unique():
                data = df[df['Tipo_Entreno'] == tipo]
                ax.scatter(data['Fecha'], data['TSS_Estimado'], 
                          label=tipo, s=100, alpha=0.6, color=colores_tipo.get(tipo, 'gray'))
            ax.set_title('TSS Estimado por Tipo de Entrenamiento', fontweight='bold', fontsize=14)
            ax.set_xlabel('Fecha')
            ax.set_ylabel('TSS Estimado')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        st.markdown("---")
        # ============================================
        # ANÁLISIS POR TIPO DE ENTRENAMIENTO
        # ============================================
        
        st.header("📈 Análisis por Tipo de Entrenamiento")
        
        dias_orden = ['Ritmo Sostenido', 'Series/Intervalos', 'Fondo']
        
        for tipo in dias_orden:
            data = df[df['Tipo_Entreno'] == tipo]
            if len(data) > 0:
                with st.expander(f"🏃 {tipo.upper()} ({len(data)} entrenamientos)"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Distancia promedio", f"{data['Distancia'].mean():.2f} km")
                    with col2:
                        st.metric("TSS Estimado promedio", f"{data['TSS_Estimado'].mean():.1f}")
                    with col3:
                        st.metric("FC media promedio", f"{data['Frecuencia cardiaca media'].mean():.0f} bpm")
                    with col4:
                        st.metric("TSB promedio al llegar", f"{data['TSB'].mean():.1f}")
                    
                    if data['TSB'].mean() < -5:
                        st.warning("⚠️ Llegás fatigado a estos entrenamientos")
        
        st.markdown("---")
        
        # ============================================
        # RECOMENDACIONES
        # ============================================
        
        st.header("💡 Recomendaciones Personalizadas")
        
        recomendaciones = []
        
        martes_data = df[df['Tipo_Entreno'] == 'Ritmo Sostenido']
        jueves_data = df[df['Tipo_Entreno'] == 'Series/Intervalos']
        sabado_data = df[df['Tipo_Entreno'] == 'Fondo']
        
        if len(jueves_data) > 0 and jueves_data['TSB'].mean() < -5:
            recomendaciones.append("📌 Los jueves llegás con fatiga acumulada. Considerá alivianar los martes.")
        
        if len(sabado_data) > 0 and sabado_data['TSB'].mean() < -5:
            recomendaciones.append("📌 Los sábados (fondos) te generan mucha fatiga. Asegurate de recuperar bien domingo-lunes.")
        
        if len(df) >= 5 and df.tail(5)['Desviacion_Eficiencia'].mean() > 5:
            recomendaciones.append("📌 Tu eficiencia cardíaca está deteriorada últimamente. Señal de fatiga acumulada.")
        
        if ultimo['ACWR'] > 1.3:
            recomendaciones.append("📌 CRÍTICO: Tu ratio de carga está alto. No aumentes volumen esta semana.")
        
        if ultimo['TSB'] < -10:
            recomendaciones.append("📌 CRÍTICO: Necesitás al menos 2-3 días de recuperación antes de entrenar duro.")
        
        if len(recomendaciones) > 0:
            for rec in recomendaciones:
                st.info(rec)
        else:
            st.success("✅ ¡Todo se ve bien! Seguí con tu plan de entrenamiento actual.")
        
        st.markdown("---")
        
        # ============================================
        # TABLA DE DATOS
        # ============================================
        
        with st.expander("📊 Ver tabla de datos completa"):
            st.dataframe(
                df[['Fecha', 'Tipo_Entreno', 'Distancia', 'TSS_Estimado', 'ATL', 'CTL', 'TSB', 'ACWR', 'Riesgo_Lesion']],
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.info("Verificá que el CSV tenga las columnas esperadas (Fecha, Distancia, TE aeróbico, etc.)")

else:
    # Mensaje de bienvenida
    st.info("👈 Subí tu archivo CSV desde el panel lateral para comenzar el análisis")
    
    st.markdown("""
    ### 🎯 ¿Qué hace esta aplicación?
    
    Esta app analiza tus entrenamientos de running para:
    - **Detectar fatiga acumulada** (ATL/CTL/TSB)
    - **Prevenir lesiones** (ACWR - Ratio Agudo:Crónico)
    - **Monitorear eficiencia cardíaca**
    - **Dar recomendaciones personalizadas**
    
    ### 📁 ¿Qué archivo necesito?
    
    Un CSV exportado desde Garmin Connect, Strava u otra plataforma con estas columnas:
    - Fecha
    - Distancia
    - TE aeróbico
    - Frecuencia cardíaca media
    - Ritmo medio
    
    ### 🔄 ¿Cómo actualizar?
    
    Cada semana, exportá un CSV actualizado y subilo aquí. ¡Así de simple!
    """)


