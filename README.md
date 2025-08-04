# Avance Preliminar del Proyecto

## 1. Información del Proyecto
- **Nombre del Proyecto:** BioHarmony
- **Equipo y Roles:** 
    - [Thomas Bermúdez Mora](https://www.linkedin.com/in/thomas-bermudez-mora/) - Líder de Calidad y Desarrollador
    - [Franklin Castro Rodriguez](https://www.linkedin.com/in/franklin-castro-rodriguez/) - Líder del Logística y Desarrollador
    - [Gabriel Lobo Ulloa](https://www.linkedin.com/in/glovooker/) - Líder Técnico y Desarrollador

## 2. Descripción y Justificación
- **Problema que se aborda:** 
    La falta de soluciones creativas y accesibles que integren tecnología e inteligencia artificial para el cuidado y monitoreo de plantas.  
- **Importancia y contexto:**  
    Combina IoT, LLMs y generación musical como forma innovadora de interpretar datos ambientales, fomentando el cuidado de plantas y la educación tecnológica.
- **Usuarios/beneficiarios:**  
    - Entusiastas de la jardinería y cuidado de plantas.
    - Centros educativos que busquen proyectos STEAM interactivos.
    - Makers y desarrolladores interesados en IoT y AI creativas.

## 3. Objetivos del Proyecto
- **Objetivo General:**  
    Desarrollar un sistema que interprete datos de luz y humedad para generar música adaptativa mediante un LLM, estimulando el crecimiento y cuidado de plantas.
- **Objetivos Específicos:**  
    - Leer e interpretar datos de sensores de luz y humedad.
    - Mapear condiciones de la planta a patrones musicales.
    - Integrar un LLM que genere interpretaciones musicales adaptativas.
    - Mostrar datos y estados en un monitor serial o interfaz visual.

## 4. Requisitos Iniciales
- Lista breve de lo que el sistema debe lograr:  
    - Medir humedad y luz de forma periódica.
    - Interpretar valores para determinar estado de la planta.
    - Generar y reproducir patrones musicales en base al estado.

## 5. Diseño Preliminar del Sistema
- **Arquitectura inicial (diagrama):**  
  *(Pendiente incluir diagrama con: Sensores → Ideaboard SP32 → LLM/API → Generador de música → Buzzer/Salida)*  

- **Componentes previstos:**  
    - **Microcontrolador:** Ideaboard SP32 (ESP32)
    - **Sensores/actuadores:** Sensor de humedad, sensor de luz (LDR), buzzer piezoeléctrico
    - **LLM/API:** OpenAI API o HuggingFace API (opcional, para interpretación avanzada)
    - **Librerías y herramientas:** Arduino IDE, librerías PWM/tone, WiFiClient, HTTPClient 

- **Bocetos o esquemas:**  
  *(Pendiente agregar diagrama simple con conexiones)*  

## 6. Plan de Trabajo
- **Cronograma preliminar:**  
    | Semana | Actividad                                     |
    | ------ | --------------------------------------------- |
    | 1      | Configuración de sensores y lectura básica    |
    | 1-2    | Implementación de patrones musicales y buzzer |
    | 2      | Integración con LLM/API y pruebas finales     |
    | 2      | Documentación y presentación del prototipo    |


- **Riesgos identificados y mitigaciones:**  
    - **Riesgo 1:** Problemas de conectividad con API → Mitigación: incluir lógica local por defecto.
    - **Riesgo 2:** Lecturas inestables en sensores → Mitigación: aplicar filtrado y calibración. 

## 7. Prototipos conceptuales (si aplica)
- **Código mínimo de prueba:**  
    - Lectura de humedad y luz en Serial Monitor.
    - Reproducción de un patrón musical básico con el buzzer.

- **Evidencia visual:**  
  *(Pendiente incluir fotos del montaje y capturas de lectura en Serial Monitor)*

