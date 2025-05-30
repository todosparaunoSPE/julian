# -*- coding: utf-8 -*-
"""
Created on Fri May 30 15:05:51 2025

@author: jahop
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Título de la app
st.title("🏥 Dashboard de Indicadores Clínicos - Hospital")

# Simulación de datos
@st.cache_data

def cargar_datos():
    np.random.seed(42)
    random_state = np.random.RandomState(42)
    n = 1000
    fechas = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    medicos = ['Dr. López', 'Dra. Martínez', 'Dr. Velázquez', 'Dra. Sánchez']
    servicios = ['Ginecología', 'Cirugía', 'Urgencias', 'Obstetricia']
    tipos_parto = ['Cesárea', 'Parto Natural']
    complicaciones = ['Ninguna', 'Infección', 'Hemorragia', 'Fiebre', 'Reingreso']

    df = pd.DataFrame({
        'ID_Paciente': [f'P{i:04d}' for i in range(n)],
        'Fecha_Ingreso': random_state.choice(fechas, n),
        'Servicio': random_state.choice(servicios, n),
        'Médico': random_state.choice(medicos, n),
        'Tipo_Parto': random_state.choice(tipos_parto, n, p=[0.4, 0.6]),
        'Complicación': random_state.choice(complicaciones, n, p=[0.7, 0.1, 0.1, 0.05, 0.05]),
        'Días_Hospitalizado': np.maximum(1, random_state.normal(3, 2, n).astype(int)),
        'Sexo': random_state.choice(['Femenino', 'Masculino'], n, p=[0.95, 0.05])
    })

    df['Fecha_Egreso'] = df['Fecha_Ingreso'] + pd.to_timedelta(df['Días_Hospitalizado'], unit='D')
    df['Reingreso_en_7_días'] = np.where(df['Complicación'] == 'Reingreso', 'Sí', 'No')
    df['Mes'] = df['Fecha_Ingreso'].dt.to_period('M').astype(str)
    return df

# Cargar datos
df = cargar_datos()

# Sidebar de filtros
st.sidebar.header("Filtros")
servicio = st.sidebar.multiselect("Servicio", options=df['Servicio'].unique(), default=df['Servicio'].unique())
medico = st.sidebar.multiselect("Médico", options=df['Médico'].unique(), default=df['Médico'].unique())
rango_fechas = st.sidebar.date_input("Rango de Fechas", [df['Fecha_Ingreso'].min(), df['Fecha_Ingreso'].max()])

# Nombre del desarrollador
st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado por: Javier Horacio Pérez Ricárdez")

# Aplicar filtros
df_filtrado = df[
    (df['Servicio'].isin(servicio)) &
    (df['Médico'].isin(medico)) &
    (df['Fecha_Ingreso'] >= pd.to_datetime(rango_fechas[0])) &
    (df['Fecha_Ingreso'] <= pd.to_datetime(rango_fechas[1]))
]

# Métricas
total_partos = df_filtrado.shape[0]
porcentaje_cesareas = round((df_filtrado['Tipo_Parto'] == 'Cesárea').mean() * 100, 2)
porcentaje_reingresos = round((df_filtrado['Reingreso_en_7_días'] == 'Sí').mean() * 100, 2)
promedio_estancia = round(df_filtrado['Días_Hospitalizado'].mean(), 2)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Partos", total_partos)
col2.metric("% Cesáreas", f"{porcentaje_cesareas}%")
col3.metric("% Reingresos", f"{porcentaje_reingresos}%")
col4.metric("Estancia Promedio (días)", promedio_estancia)

# Gráficos
st.subheader("Distribución de Tipo de Parto")
fig1 = px.pie(df_filtrado, names='Tipo_Parto', title='Tipo de Parto')
st.plotly_chart(fig1)

st.subheader("Complicaciones por Servicio")
fig2 = px.histogram(df_filtrado, x='Servicio', color='Complicación', barmode='group', title='Complicaciones por Servicio')
st.plotly_chart(fig2)

st.subheader("Tendencia Mensual de Partos")
partos_mensuales = df_filtrado.groupby('Mes').size().reset_index(name='Cantidad')
fig3 = px.line(partos_mensuales, x='Mes', y='Cantidad', markers=True, title='Partos por Mes')
st.plotly_chart(fig3)

# Tabla
st.subheader("Datos Detallados")
st.dataframe(df_filtrado.sort_values(by='Fecha_Ingreso', ascending=False))
