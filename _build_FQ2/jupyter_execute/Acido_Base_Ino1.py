#!/usr/bin/env python
# coding: utf-8

# # Acidos monopróticos

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def gradient_fill(x, y_min, y_max, color_sup = 'blue', color_inf='red', alpha_sup = 1, alpha_inf = 1, **kwargs):
  '''Función auxiliar que colorea la zona de viraje de un indicador
  con los colores correspondientes'''
  z = np.empty((100, 1, 4), dtype=float)
  rgb = mcolors.colorConverter.to_rgb(color_sup)
  z[:,:,:3] = rgb
  z[:,:,-1] = np.linspace(0, alpha_sup, 100)[:,None]
    
  xmin, xmax, ymin, ymax = x.min(), x.max(), y_min, y_max
  im = plt.imshow(z, aspect='auto', extent=[xmin, xmax, ymin, ymax],
                   origin='lower')
    
  z2 = np.empty((100, 1, 4), dtype=float)
  rgb2 = mcolors.colorConverter.to_rgb(color_inf)
  z2[:,:,:3] = rgb2
  z2[:,:,-1] = np.linspace(alpha_inf, 0, 100)[:,None]
    
  xmin, xmax, ymin, ymax = x.min(), x.max(), y_min, y_max
  im2 = plt.imshow(z2, aspect='auto', extent=[xmin, xmax, ymin, ymax],
                   origin='lower')


# In[2]:


get_ipython().run_line_magic('matplotlib', 'inline')
#from ipywidgets import interactive
import ipywidgets as widgets
from ipywidgets import interactive, FloatSlider, HBox, Layout,VBox
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

#plt.rcParams['axes.facecolor']='white'

def grado2(PH,km,Cm,Ct,es_acido):
    kw = 1E-14
    H = 10**(-PH)
    OH = kw/H
    if es_acido == 'Ácido':
        primero = km / (km + H)
        segundo = (H - OH) / Cm
        tercero = (H - OH) / Ct
    else:
        primero = km / (km + OH)
        segundo = - (H - OH) / Cm
        tercero = - (H - OH) / Ct
    
    #print(pH[p], H, OH)
    grado = (primero - segundo )/(1 + tercero)
    if grado <= 0:
        grado = 0
    #elif grado > 3:
    #    grado = 3
    return grado 

def titulacion2(es_acido, Cm, Ct, pKm, Va, indicador):
    ''' Curva de tilación simple, titulación de acido monoprótico débilcon base fuerte
    Entrada:
    Cm: concentración de la muestra (sea ácido o base) (Molar), float
    Ct: concentración del titulante (sea base o ácido) (Molar), float
    pKm: Valor de pK de la muestra, float
    Va: volumen de la muestra (debería cambiarlo a Vm) en mL, float
    indicador: nombre del indicador usado de una lista predeterminada, str
    
    Se crea un array de pH entre ciertos pH limite de acuerdo al acido y base utilizados,
    con eso se calcula el volumen de base (Vb) necesario y se grafica la curva con algunos
    puntos de interés y si se indica un indicador te muestra la zona de viraje
    Tras elegir un indicador, además calcula la diff. % entre pto equivalencia y punto final.
    Si se titula un ácido o una base, los nombres de los widgets cambian en función de eso
    
    '''
    kw = 1E-14
    Km = 10**(-pKm)
    # cálculo de pH límites
    if es_acido == 'Ácido':
        pHlim_sup = 14 + np.log10(Ct)
        pHlim_inf = (pKm - np.log10(Cm))/2
    else:
        pHlim_sup = 14 -(pKm - np.log10(Cm))/2
        pHlim_inf = - np.log10(Ct)
    #print('pH_sup:', round(pHlim_sup,2), 'pH_inf:', round(pHlim_inf,2))
    pH = np.linspace(pHlim_inf+0.01, pHlim_sup-0.01, num=29).tolist()
    
    
    Vb = []
    Veq = Va*Cm/Ct
    for p in range(len(pH)):
        grad = grado2(pH[p],Km,Cm,Ct,es_acido)
        Vb.append(grad*Veq) # volumen agregado para alcanzar cierto pH
        Ct_eq = Veq*Ct/(Veq + Va)
        #cálculo de pH del punto de equivalencia segun es ácido o base
        if es_acido == 'Ácido':
            pHeq = round(14 + (np.log10(kw*Ct_eq/Km)/2),2) 
        else:
            pHeq = round(- np.log10(kw*Ct_eq/Km)/2,2)
    plt.figure()
    plt.plot(Vb, pH, color='black', label='Curva de Titulación')
    plt.vlines(Veq, ymin = 0, ymax = pHeq, color='g', linestyle='dashed', alpha = 0.5,
                label=r'$V_{eq} = $'+str(round(Veq,2))+ 'mL')
    plt.hlines(y=pHeq, xmin=0, xmax =Veq, color='b', linestyle='dashed', alpha = 0.5,
               label=r'$pH_{eq} = $'+str(pHeq))
    # ********* Indicadores ******************
    indicadores = {'Azul de timol':['red', 'yellow', 1.2,2.8, 0.8,0.8], 
                   'Naranja de metilo':['red', 'orange',3.1,4.4, 1, 0.7],
                   'Rojo de metilo':['red', 'yellow', 4.4, 6.2, 0.8,0.8],
                   'Azul de bromofenol':['yellow', 'blue',6.2, 7.6,0.8, 0.8],
                   'Fenolftaleina':['white','fuchsia', 8, 10,0.8,0.8], 
                   'Amarillo de alizarina':['yellow', 'purple', 10, 12,0.8,0.8]}
    pF = 0
    if indicador != 'Ninguno':
        color_sup = indicadores[indicador][0]
        color_inf = indicadores[indicador][1]
        lim_inf = indicadores[indicador][2]
        lim_sup = indicadores[indicador][3]
        alpha_inf = indicadores[indicador][4]
        alpha_sup = indicadores[indicador][5]
        gradient_fill(np.array(Vb), lim_inf , lim_sup, color_inf, color_sup,alpha_inf , alpha_sup)
        
        if es_acido == 'Ácido':
            pF = min(lim_inf-pHlim_inf,lim_sup-pHlim_inf) 
            pF_aux = pHlim_inf
        else:
            pF = min(pHlim_sup - lim_sup,pHlim_sup - lim_inf) 
            pF_aux = -pHlim_sup
    
    #******* Imprime resultados de punto final *************
    if indicador == 'Ninguno':
        print('No se eligió indicador')
    elif pF <= 0:
        print('Error en punto final')
    else:
        pF = abs(pF + pF_aux)
        Vf = grado2(pF,Km,Cm,Ct,es_acido)*Veq
        Cmf = Ct*Vf/Va
        print(tabulate([['pH punto final:', pF,], ['Dif. pH con punto equivalencia:', round(abs(pF - pHeq),2),],
               ['Dif.rel.% volumen punto equivalencia:', round(abs(Vf - Veq)/Veq*100,1),'%'], 
                        ['C.muestra por punto final', round(Cmf,3),'M'],
               ['Dif.rel.% en C.muestra',round(abs(Cmf - Cm)/Cm*100,1),'%']], headers=['Resultados', 'Valor', 'Unidad']
             , tablefmt='orgtbl'))
        
        plt.vlines(Vf, ymin = 0, ymax = pF, color='g', linestyle='solid', alpha = 0.5,
                label=r'$V_{P.final} = $'+str(round(Vf,2))+ 'mL')
    plt.xlim(0,2*Veq)
    plt.ylim(0, 14)
    plt.ylabel('pH', size = 12)
    plt.xlabel(r'$V_{base\ fuerte}\ (mL)$', size = 12)
    plt.legend(loc = 'best', bbox_to_anchor=(1.5, 0.5))#, frameon = 'True')
    #plt.xticks(np.arange(0, 2*Veq+1, step=(int(2*Veq / 14) + (2*Veq % 14 > 0))))
    plt.yticks(np.arange(0, 14+1, step=1))
    plt.show()
    
    if es_acido == 'Ácido':
        Va_display.description='Volúmen Ácido (mL)'
        Cm_display.description='Concentración Ácido (M)'
        Ct_display.description='Concentración Base (M)'
        pKm_display.description='pK Ácido'
    else:
        Va_display.description='Volúmen Base (mL)'
        Cm_display.description='Concentración Base (M)'
        Ct_display.description='Concentración Ácido (M)'
        pKm_display.description='pK Base'

# widgets para cada variable, opciones de configuración, rango de valores que toma cada parámetro y nombre predeterminado.

es_acido_widget = widgets.ToggleButtons(layout = {'width':'max-content'}, style = {'description_width':'150px'},
    description='Tipo de muestra',
    options=['Ácido', 'Base'],
)
Va_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                              options=np.arange(1,10,1),value=5, description='$V_{muestra}$'+' (mL)',)
Cm_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                              options=np.arange(0.01,1,0.03).round(2),value=0.1,description='$C_{muestra}$'+' (M)',) 
Ct_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                              options=np.arange(0.01,1,0.03).round(2), value=0.1,description='$C_{titulante}$'+' (M)',) 
pKm_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                               options=np.arange(1,9,0.25),value=4.75, description='$pK_{muestra}$',)
Indicador = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
    options=['Ninguno','Azul de timol', 'Naranja de metilo', 'Rojo de metilo', 'Azul de bromofenol', 
             'Fenolftaleina', 'Amarillo de alizarina'], value='Ninguno',
    description='Indicador',)

# aca se utiliza la función interactive que lee los widgets anteriores todo el tiempo y con esos datos va a titulación2
interactive_plot  = interactive(titulacion2, Cm=Cm_display, Ct=Ct_display, pKm = pKm_display, Va=Va_display, 
                               indicador = Indicador, es_acido=es_acido_widget)

output = interactive_plot.children[-1]
output.layout.height = '500px'
interactive_plot


# Idem anterior pero le agregué una opción para agregar el volumen final utilizado por los alumnos y que se calcule el error respecto al valor téórico con eso.

# In[3]:


# Tratando de ordenar los widgets de manera específica: Tarea no exitosa actualmente, parece que todo lo que
#refiere a formato de la interfase en realidad es algo en CSS que le dice al explorador donde y como poner las cosas

import base64
import io
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display

# funciones auxiliares

def grado2(PH,km,Cm,Ct,es_acido):
    kw = 1E-14
    H = 10**(-PH)
    OH = kw/H
    if es_acido == 'Ácido':
        primero = km / (km + H)
        segundo = (H - OH) / Cm
        tercero = (H - OH) / Ct
    else:
        primero = km / (km + OH)
        segundo = - (H - OH) / Cm
        tercero = - (H - OH) / Ct
    
    #print(pH[p], H, OH)
    grado = (primero - segundo )/(1 + tercero)
    if grado <= 0:
        grado = 0
    #elif grado > 3:
    #    grado = 3
    return grado 


def titulacion2(es_acido, Cm, Ct, pKm, Va, indicador,Exp, VPF):
    ''' Idem idem anterior:
    Modificación: Ahora podes agregar el volumen del punto final que determinan los estudiantes
    Para así comparar el error del método (asociado a la elección del indicador) vs el error humano, y
    que ese error está asociado con una diferencia de pH enorme
    '''
    
    kw = 1E-14
    Km = 10**(-pKm)
    # calculo de pH límites
    if es_acido == 'Ácido':
        pHlim_sup = 14 + np.log10(Ct)
        pHlim_inf = (pKm - np.log10(Cm))/2
    else:
        pHlim_sup = 14 -(pKm - np.log10(Cm))/2
        pHlim_inf = - np.log10(Ct)
    #print('pH_sup:', round(pHlim_sup,2), 'pH_inf:', round(pHlim_inf,2))
    pH = np.linspace(pHlim_inf+0.01, pHlim_sup-0.01, num=29).tolist()
    
    Vb = []
    Veq = Va*Cm/Ct
    for p in range(len(pH)):
        grad = grado2(pH[p],Km,Cm,Ct,es_acido)
        Vb.append(grad*Veq)
        Ct_eq = Veq*Ct/(Veq + Va)
        if es_acido == 'Ácido':
            pHeq = round(14 + (np.log10(kw*Ct_eq/Km)/2),2)
        else:
            pHeq = round(- np.log10(kw*Ct_eq/Km)/2,2)
    plt.figure()
    plt.plot(Vb, pH, color='black', label='Curva de Titulación')
    plt.vlines(Veq, ymin = 0, ymax = pHeq, color='g', linestyle='dashed', alpha = 0.5,
                label=r'$V_{eq} = $'+str(round(Veq,2))+ 'mL')
    plt.hlines(y=pHeq, xmin=0, xmax =Veq, color='b', linestyle='dashed', alpha = 0.5,
               label=r'$pH_{eq} = $'+str(pHeq))
    # ********* Indicadores ******************
    indicadores = {'Azul de timol':['red', 'yellow', 1.2,2.8, 0.8,0.8], 
                   'Naranja de metilo':['red', 'orange',3.1,4.4, 1, 0.7],
                   'Rojo de metilo':['red', 'yellow', 4.4, 6.2, 0.8,0.8],
                   'Azul de bromofenol':['yellow', 'blue',6.2, 7.6,0.8, 0.8],
                   'Fenolftaleina':['white','fuchsia', 8, 10,0.8,0.8], 
                   'Amarillo de alizarina':['yellow', 'purple', 10, 12,0.8,0.8]}
    pF = 0
    if indicador != 'Ninguno':
        color_sup = indicadores[indicador][0]
        color_inf = indicadores[indicador][1]
        lim_inf = indicadores[indicador][2]
        lim_sup = indicadores[indicador][3]
        alpha_inf = indicadores[indicador][4]
        alpha_sup = indicadores[indicador][5]
        gradient_fill(np.array(Vb), lim_inf , lim_sup, color_inf, color_sup,alpha_inf , alpha_sup)
        
        if es_acido == 'Ácido':
            pF = min(lim_inf-pHlim_inf,lim_sup-pHlim_inf) 
            pF_aux = pHlim_inf
        else:
            pF = min(pHlim_sup - lim_sup,pHlim_sup - lim_inf) 
            pF_aux = -pHlim_sup
    
    #******* Imprime resultados de punto final *************
    if indicador == 'Ninguno':
        print('No se eligió indicador')
    elif pF <= 0:
        print('Error en punto final')
    else:
        # Checkbox de experimento: 
        #Seleccionado indica que se corrió el experimento y que se agregará un volumen de punto final externo
        # No seleccionado: no se corrió experimento y se calcula el punto final teórico del indicador
        if exp_check.value == False:
            pF = abs(pF + pF_aux)
            Vf = grado2(pF,Km,Cm,Ct,es_acido)*Veq
            Vfinal_widget.value = round(Vf,2)
        else:
            Vf = Vfinal_widget.value
            pF = round(pH[(np.abs(Vb - np.float64(Vf))).argmin()],2)
            
        Cmf = Ct*Vf/Va  # concentración de la muestra calculada segun punto final
        print(tabulate([['pH punto final:', pF,], ['Dif. pH con punto equivalencia:', round(abs(pF - pHeq),2),],
               ['Dif.rel.% volumen punto equivalencia:', round(abs(Vf - Veq)/Veq*100,1),'%'], 
                        ['C.muestra por punto final', round(Cmf,3),'M'],
               ['Dif.rel.% en C.muestra',round(abs(Cmf - Cm)/Cm*100,1),'%']], headers=['Resultados', 'Valor', 'Unidad']
             , tablefmt='orgtbl'))
        
        plt.vlines(Vf, ymin = 0, ymax = pF, color='g', linestyle='solid', alpha = 0.5,
                label=r'$V_{P.final} = $'+str(round(Vf,2))+ 'mL')
    plt.xlim(0,2*Veq)
    plt.ylim(0, 14)
    plt.ylabel('pH', size = 12)
    plt.xlabel(r'$V_{base\ fuerte}\ (mL)$', size = 12)
    plt.legend(loc = 'best', bbox_to_anchor=(1.5, 0.5))#, frameon = 'True')
    #plt.xticks(np.arange(0, 2*Veq+1, step=(int(2*Veq / 14) + (2*Veq % 14 > 0))))
    plt.yticks(np.arange(0, 14+1, step=1))
    plt.show()
    
    if es_acido == 'Ácido':
        Va_display.description='Volúmen Ácido (mL)'
        Cm_display.description='Concentración Ácido (M)'
        Ct_display.description='Concentración Base (M)'
        pKm_display.description='pK Ácido'
    else:
        Va_display.description='Volúmen Base (mL)'
        Cm_display.description='Concentración Base (M)'
        Ct_display.description='Concentración Ácido (M)'
        pKm_display.description='pK Base'

# widgets para cada variable, opciones de configuración, rango de valores que toma cada parámetro y nombre predeterminado.

es_acido_widget = widgets.ToggleButtons(layout = {'width':'max-content'}, style = {'description_width':'150px'},
    description='Tipo de muestra',
    options=['Ácido', 'Base'],
)
#Va_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
#                              options=np.arange(1,10,1),value=5, description='$V_{muestra}$'+' (mL)',)
Va_display = widgets.BoundedFloatText(layout = {'width':'25%'}, style = {'description_width':'150px'},
                value=2.0, min=0.1,max=20.0,step=0.1, description='$V_{muestra}$'+' (mL)')
#Cm_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
#                              options=np.arange(0.01,1,0.03).round(2),value=0.1,description='$C_{muestra}$'+' (M)',)
Cm_display = widgets.BoundedFloatText(layout = {'width':'25%'}, style = {'description_width':'150px'},
                value=0.1, min=0.01,max=1,step=0.01, description='$C_{muestra}$'+' (M)')
#Ct_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
#                              options=np.arange(0.01,1,0.03).round(2), value=0.1,description='$C_{titulante}$'+' (M)',) 
Ct_display = widgets.BoundedFloatText(layout = {'width':'25%'}, style = {'description_width':'150px'},
                value=0.1, min=0.01,max=1,step=0.01, description='$C_{titulante}$'+' (M)')

pKm_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                               options=np.arange(1,9,0.25),value=4.75, description='$pK_{muestra}$',)
Indicador = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
    options=['Ninguno','Azul de timol', 'Naranja de metilo', 'Rojo de metilo', 'Azul de bromofenol', 
             'Fenolftaleina', 'Amarillo de alizarina'], value='Ninguno',
    description='Indicador',)

Vfinal_widget = widgets.BoundedFloatText(layout = {'width':'25%'}, style = {'description_width':'150px'},
                value=0, min=0,max=20.0,step=0.1, description='Volumen punto final (mL):',disabled=False)

exp_check = widgets.Checkbox(value=False, description='Experimento',disabled=False,indent=True,
                             layout = {'width':'max-content'}, style = {'description_width':'150px'})

# aca se utiliza la función interactive que lee los widgets anteriores todo el tiempo y con esos datos va a titulación2
interactive_plot  = interactive(titulacion2, Cm=Cm_display, Ct=Ct_display, pKm = pKm_display, Va=Va_display, 
                               indicador = Indicador, es_acido=es_acido_widget, Exp = exp_check, VPF = Vfinal_widget)

output = interactive_plot.children[-1]
output.layout.height = '500px'
interactive_plot


# #Curva de titulación de Acidos polipróticos

# In[4]:


import matplotlib.pyplot as plt
import ipywidgets as widgets
from ipywidgets import interactive
from IPython.display import display
import numpy as np
from tabulate import tabulate
from scipy.optimize import curve_fit


def grado_poli(PH,ka1,ka2,ka3,Ca,Cb):
    kw = 1E-14
    H = 10**(-PH)
    OH = kw/H
    alfa_1 = ka1*ka2*ka3/(H**3 + ka1*H**2 + ka1*ka2*H + ka1*ka2*ka3)
    alfa_2 = alfa_1*H/ka3
    alfa_3 = alfa_2*H/ka2
    #print(pH[p], H, OH)
    grado = ((3*alfa_1 + 2*alfa_2 + alfa_3)*Cb - (H - OH)*Cb/Ca)/(H - OH + Cb)
    
    if grado <= 0:
        grado = 0
    #elif grado > 3:
    #    grado = 3
    return grado 

def titulacion_poli(Ca, Cb, pKa1, pKa2, pKa3, Va,indicador):
    pHlim_sup = 14 + np.log10(Cb)
    pHlim_inf = (pKa1 - np.log10(Ca))/2
    pH = np.linspace(pHlim_inf+0.01, pHlim_sup-0.01, num=59).tolist()
    
    kw = 1E-14
    ka1 = 10**(-pKa1)
    ka2 = 10**(-pKa2)
    ka3 = 10**(-pKa3)
    Vb = []
    Veq1 = Va*Ca/Cb
    Veq2 = Veq1*2
    Veq3 = Veq1*3

    for p in range(len(pH)):
        grad = grado_poli(pH[p],ka1, ka2, ka3,Ca,Cb)
        Vb.append(grad*Veq1)
    #idx = np.argwhere(np.diff(np.sign(np.array(Vb) - np.array([Veq1]*59)))).flatten()
    
    # ¿Calcular el pH del punto de equivalencia de un poliprótico como un químico? Noooo, 
    # ¿Pedirle a python el valor mas cercano al volumen de equivalencia? Siiii.
    pHeq1 = round(pH[(np.abs(Vb - Veq1)).argmin()],2)
    pHeq2 = round(pH[(np.abs(Vb - Veq2)).argmin()],2)
    pHeq3 = round(pH[(np.abs(Vb - Veq3)).argmin()],2)
        
    plt.figure()
    plt.plot(Vb, pH, color='black', label='Curva de Titulación')
    plt.vlines(Veq1, ymin = 0, ymax = pHeq1, color='g', linestyle='dashed', alpha = 0.5,
                label=r'$V_{eq,1} = $'+str(round(Veq1,2))+ 'mL')
    plt.hlines(y=pHeq1, xmin=0, xmax =Veq1, color='b', linestyle='dashed', alpha = 0.5,
               label=r'$pH_{eq,1} = $'+str(pHeq1))
    plt.vlines(Veq2, ymin = 0, ymax = pHeq2, color='g', linestyle='dashed', alpha = 0.5,
                label=r'$V_{eq,2} = $'+str(round(Veq2,2))+ 'mL')
    plt.hlines(y=pHeq2, xmin=0, xmax =Veq2, color='b', linestyle='dashed', alpha = 0.5,
               label=r'$pH_{eq,2} = $'+str(pHeq2))
    plt.vlines(Veq3, ymin = 0, ymax = pHeq3, color='g', linestyle='dashed', alpha = 0.5,
                label=r'$V_{eq,3} = $'+str(round(Veq3,2))+ 'mL')
    plt.hlines(y=pHeq3, xmin=0, xmax =Veq3, color='b', linestyle='dashed', alpha = 0.5,
               label=r'$pH_{eq,2} = $'+str(pHeq3))
    # ********* Indicadores ******************
    indicadores = {'Azul de timol':['red', 'yellow', 1.2,2.8, 0.8,0.8], 
                   'Naranja de metilo':['red', 'orange',3.1,4.4, 1, 0.7],
                   'Rojo de metilo':['red', 'yellow', 4.4, 6.2, 0.8,0.8],
                   'Azul de bromofenol':['yellow', 'blue',6.2, 7.6,0.8, 0.8],
                   'Fenolftaleina':['white','fuchsia', 8, 10,0.8,0.8], 
                   'Amarillo de alizarina':['yellow', 'purple', 10, 12,0.8,0.8]}
    pF = 0
    if indicador != 'Ninguno':
        color_sup = indicadores[indicador][0]
        color_inf = indicadores[indicador][1]
        lim_inf = indicadores[indicador][2]
        lim_sup = indicadores[indicador][3]
        alpha_inf = indicadores[indicador][4]
        alpha_sup = indicadores[indicador][5]
        gradient_fill(np.array(Vb), lim_inf , lim_sup, color_inf, color_sup,alpha_inf , alpha_sup)
        
        
        pF = min(lim_inf-pHlim_inf,lim_sup-pHlim_inf) 
        pF_aux = pHlim_inf
    
    #******* Imprime resultados de punto final *************
    #if indicador == 'Ninguno':
    #    print('No se eligió indicador')
    #elif pF <= 0:
    #    print('Error en punto final')
    #else:
    if indicador != 'Ninguno':
        pF = abs(pF + pF_aux)
        Vf = grado_poli(pF,ka1, ka2, ka3,Ca,Cb)*Veq1
        Caf = Cb*Vf/Va
        #print(tabulate([['pH punto final:', pF,], ['Dif. pH con punto equivalencia:', round(abs(pF - pHeq1),2),],
        #       ['Dif.rel.% volumen punto equivalencia:', round(abs(Vf - Veq1)/Veq1*100,1),'%'], 
        #                ['C.muestra por punto final', round(Caf,3),'M'],
        #       ['Dif.rel.% en C.muestra',round(abs(Caf - Ca)/Ca*100,1),'%']], headers=['Resultados', 'Valor', 'Unidad']
        #     , tablefmt='orgtbl'))
        
        plt.vlines(Vf, ymin = 0, ymax = pF, color='g', linestyle='solid', alpha = 0.5,
                label=r'$V_{P.final} = $'+str(round(Vf,2))+ 'mL')
    plt.xlim(0,4*Veq1)
    plt.ylim(0, 14)
    plt.ylabel('pH', size = 12)
    plt.xlabel(r'$V_{base\ fuerte}\ (mL)$', size = 12)
    plt.legend(loc = 'best', bbox_to_anchor=(1.5, 0.5))#, frameon = 'True')
    #plt.xticks(np.arange(0, 2*Veq+1, step=(int(2*Veq / 14) + (2*Veq % 14 > 0))))
    plt.yticks(np.arange(0, 14+1, step=1))
    #plt.plot(Vb[idx], pH[idx], 'ro')
    #print(pH[idx[0]])


Va_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                              options=np.arange(1,10,1),value=5, description='Volúmen Ácido (mL)',)
Ca_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                              options=np.arange(0.01,1,0.03).round(2),value=0.1,description='Concentración Ácido (M)',) 
Cb_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                              options=np.arange(0.01,1,0.03).round(2), value=0.1,description='Concentración Base (M)',) 
pK1_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                               options=np.arange(1,5,0.25),value=2.0, description='pK Ácido 1',)
pK2_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                               options=np.arange(2,9,0.25),value=6.0, description='pK Ácido 2',)
pK3_display = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
                               options=np.arange(7,13,0.25),value=9.0, description='pK Ácido 3',)
Indicador = widgets.Dropdown(layout = {'width':'max-content'}, style = {'description_width':'150px'},
    options=['Ninguno','Azul de timol', 'Naranja de metilo', 'Rojo de metilo', 'Azul de bromofenol', 
             'Fenolftaleina', 'Amarillo de alizarina'], value='Ninguno',
    description='Indicador',)

# aca se utiliza la función interactive que lee los widgets anteriores todo el tiempo y con esos datos va a titulación2
interactive_plot  = interactive(titulacion_poli, Ca=Ca_display, Cb=Cb_display, pKa1 = pK1_display, pKa2 = pK2_display,
                 pKa3 = pK3_display,Va=Va_display, indicador = Indicador)


output = interactive_plot.children[-1]
output.layout.height = '400px'
interactive_plot

# otras ideas: Poner solo pKas de cosas existentes o poner una lista de ácidos polipróticos existentes


# # Simulación Buffer
# ```
# Preliminar de la parte del TP de Acido-Base donde le agregan volúmenes de NaOH o HCl a distintas diluciones de buffer. 
# 
# Las funciones tienes aproximaciones y funcionan solo dentro de un rango de concentraciones y pKas que si bien son coherentes, es un poco restrictivo. Actualmente está hecho para un buffer con pH = pKa
# ```
# 
# 

# In[5]:


get_ipython().run_line_magic('matplotlib', 'inline')
import ipywidgets as widgets
from ipywidgets import interactive, FloatSlider, HBox, Layout,VBox
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np

def grado(PH,km,Cm,Ct):
    '''
    Calcula el grado de la titulación entre una muestra y un titulante.
    La muestra pueden ser ácido o base débil.
    El titulante puede ser una base o ácido fuerte, según la muestra.
    Grado es función del pH y es la relación en moles de titulante respecto
    los moles de la muestra. Es igual a 1 cuando se alcanza el punto de equivalencia.
    
    ---------------
    Argumentos:
    pH: valor de pH, variable independiente, float
    km: constante de la muestra (puede ser un Ka o un Kb), float
    Cm: concentración inicial de la muestra en Molar, float
    Ct: concentración inicial del titulante en Molar, float
    
    ----------------
    Devuelve:
    Grado: float entre 0 y infinito
    '''
    # definición de parámetros auxiliares
    kw = 1E-14 
    H = 10**(-PH)
    OH = kw/H
    
    # Se utiliza una ecuación de segundo grado válido para todo el rango de pH
    # No realiza aproximaciones, a excepción de coeficiente de actividad = 1
    primero = km / (km + H)
    segundo = (H - OH) / Cm
    tercero = (H - OH) / Ct
    
    grado = (primero - segundo )/(1 + tercero)
   
    return grado 

def pH_acido(Va,Km,Cm,Ca,Cnt,Vm,Vnt):
    '''
    Calcula el pH de la titulación entre un "buffer" y un titulante, ambos ácidos.
    El titulante es un ácido fuerte.
    El pH obtenido es función del volúmen (en mL) del acido fuerte agregado.
    
    ---------------
    Argumentos:
    Va: volumen del ácido fuerte utilizado, float
    Vm: volumen inicial (mL) del ácido débil usado para preparar el buffer, float
    Ca: concentración inicial del ácido fuerte en Molar, float
    Cm: concentración inicial de la muestra en Molar, float
    km: constante de la muestra (puede ser un Ka o un Kb), float
    Cnt: concentración inicial de la base fuerte usada para preparar el buffer, float
    Vnt: volumen inicial (mL) de la base fuerte usada para preparar el buffer, float
    
    ----------------
    Devuelve:
    pH de la mezcla entre el "buffer" y el ácido fuerte, float entre 0 y 14
    '''
    # Se utiliza una ecuación de segundo grado válido para solo el rango de pH ácido
    # Se desprecia OH frente a H
    Vt = Va + Vm + Vnt # volumen total
    A = Ca*Va/Vt # concetración final de ácido fuerte
    HA = Cm*Vm/Vt # concentración final del ácido débil que forma el buffer
    B = Cnt*Vnt/Vt # concentración final de la base usada para formar el buffer
    
    a = 1 # parámetro a de la resolvente cuadrática
    b = B - A + Km # parámetro b 
    c = Km*(B - HA - A) # parámetro c
    H = (- b + np.sqrt(b**2 - 4*a*c))/(2*a) #concentración de protones
    return - np.log10(H)
   


def capacidad_buffer(Cm, Vm, pKm, Ca):
    ''' 
    Genera un gráfico de pH vs Volumen agregado de Ácido, y de Base (dos curvas)
    Ambos agregados son fuertes
    El pH obtenido es función del volúmen (en mL) del agregado.
    ---------------
    Argumentos:
    Cm: concentración inicial de la muestra en Molar, float
    Vm: volumen inicial (mL) del ácido débil usado para preparar el buffer, float
    pKm: -log10 de la constante de la muestra (puede ser un Ka o un Kb), float
    Ca: concentración inicial del ácido fuerte en Molar, float
    
    ----------------
    No devuelve variables
    '''
    # Ca y Cm no pueden ser 0. De serlo, se reemplazan por un valor cercano a cero.
    if Ca == 0:
        Ca_display.value = Ca = 0.01
    if Cm == 0:
        Cm_display.value = Cm = 0.1
    
    # definición de parámetros auxiliares
    kw = 1E-14
    Km = 10**(-pKm)
    
    Cb = Ca # Para simplificar, se toma la concentración inicial del agregado básico = agr. ácido

    pH_buffer = pKm # El mayor poder buffer es a pH = pKa. El buffer preparado tendrá ese pH inicialmente
    Veq_base = Vm*Cm/Cb # Volumen de base al cual se igualan los moles de base con los del acido debil
    Veq_acido = Vm*Cm/Ca # Volumen de ácido al cual se igualan los moles de ácido con los del acido debil
    Cnt = Cb # concentración de la base fuerte usada para armar el buffer. Para simplificar, se toma igual a Cb
    Vnt = grado(pH_buffer,Km,Cm,Cb)*Veq_base # Volumen de la base fuerte usada para armar el buffer.

    # Agregado de Base - Curva 1
    pHlim_sup = 14 + np.log10(Cb) # pH máximo posible, dado por la base fuerte usada
        #Lista de pHs: variable independiente, generada entre los limites en los que vale la curva
    pH = np.linspace(pH_buffer, pHlim_sup-0.01, num=59).tolist()
        #Lista de Volumenes de base: variable independiente, sera calculada a continuacion
    Vb = []
    for p in range(len(pH)):
        grad = grado(pH[p],Km,Cm,Cb) # Se obtiene Grado(pH). Para convertirlo en Vol. se multiplicara por Veq.
        Vb.append(grad*Veq_base - Vnt) # Se resta el vol. de base previamente usado para armar el buffer
        
    # Agregado de Ácido - Curva 2
        #Lista de Va's: variable independiente, generada entre 0 y un valor abritrario
    Va = np.linspace(0, 3*Vm, num=1000).tolist()
        #Lista de pHs: variable dependiente
    pHacido = []
    for v in range(len(Va)):
        pHacido.append(pH_acido(Va[v],Km,Cm,Ca,Cnt,Vm,Vnt))
    
    # Grafico las curvas de Ácido y Base
    plt.figure()
    
    plt.plot(Vb, pH, color='red', label='Agregado de NaOH')
    plt.plot(Va, pHacido, color='blue', label='Agregado de HCl')
    
    plt.hlines(y=pKm+1, xmin=0, xmax =2*Vm, color='black', linestyle='dashed', alpha = 0.5,
               label=r'$pKa +/- 1$')
    plt.hlines(y=pKm-1, xmin=0, xmax =2*Vm, color='black', linestyle='dashed', alpha = 0.5)#,
               #label=r'$pKa - 1$')
    plt.xlim(0,2*Vm)
    plt.ylim(0, 14)
    plt.ylabel('pH', size = 12)
    plt.xlabel(r'$V_{HCl\ /\ NaOH}\ (mL)$', size = 12)
    plt.legend(loc = 'best')
    plt.yticks(np.arange(0, 14+1, step=1))
    
    plt.show()
    
# Creo los Widgets con las variables que el usuario puede modificar
Vm_display = widgets.BoundedFloatText(max=100,min=0,step=0.5,value=5, layout = {'width':'320px'}, 
                        style = {'description_width':'250px'}, description='Volúmen muestra (mL)',)
Ca_display = widgets.BoundedFloatText(max=2,min=0,step=0.01, value=0.1, layout = {'width':'320px'}, 
                        style = {'description_width':'250px'},description='Concentración HCl/NaOH (M)',)
Cm_display =  widgets.BoundedFloatText(max=2,min=0,step=0.01, value=0.1, layout = {'width':'320px'}, 
                        style = {'description_width':'250px'},description='Concentración Buffer (M)',) 
pKm_display = widgets.BoundedFloatText(max=11,min=-2,step=0.1, value=4.75, layout = {'width':'320px'}, 
                        style = {'description_width':'250px'}, description='pK Buffer',)

# Se utiliza la función interactive que lee los widgets anteriores todo el tiempo y con esos datos ejecuta capacidad_buffer()
interactive_plot  = interactive(capacidad_buffer, Cm=Cm_display, pKm = pKm_display, Ca=Ca_display, 
                                Vm = Vm_display)
# Para mostrar el resultado
output = interactive_plot.children[-1]
output.layout.height = '500px'
interactive_plot

