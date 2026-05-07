# Q-economía: sistema económico completo para una moneda de valor de línea

**Idioma:** Español  
**Versión:** 1.0  
**Base:** La moneda está formada por monedas Q. La altura de la fila es el valor de la moneda.

---

## 1. Idea central

La Q-economía es un orden monetario, crediticio y productivo de carácter semántico. No trata solo el dinero como unidad económica, sino también la dificultad, la estructura, el código, las interfaces, la arquitectura, la operación y los módulos terminados.

Una moneda es una fila de tabla. **La altura de la fila** es su valor. **La numeración** es su acuñación. El texto del continuo es su respaldo semántico.

```text
Moneda Qn = (número n, valor h, significado B)
Valor(Qn) = altura de fila h
Significado(Qn) = contenido semántico en el continuo
```

Q20 no significa “veinte unidades”. Q20 es la moneda acuñada con el número 20 y con valor 4. Cuatro monedas Q1 pueden tener el mismo valor nominal que una moneda Q20, pero no cumplen la misma función.

---

## 2. Unidades básicas

La unidad básica se llama **valor de línea**.

```text
1 VL = 1 valor de línea
```

Como subunidad puede usarse el **octadegramo**:

```text
1 VL = 18 octadegramos
```

Por tanto:

```text
Valor 1 = 1 VL = 18 octadegramos
Valor 2 = 2 VL = 36 octadegramos
Valor 3 = 3 VL = 54 octadegramos
Valor 4 = 4 VL = 72 octadegramos
```

---

## 3. Catálogo de monedas

| Moneda | Valor | Capa | Significado económico |
|---:|---:|---|---|
| Q1 | 1 | Dificultad básica | tarea, dificultad, nudo, núcleo del problema |
| Q2 | 1 | Complejidad | parte, complicación, elemento molecular, subestructura |
| Q3 | 1 | Abstracción | teoría, modelo, estado intermedio entre suelto y fijo |
| Q4 | 1 | Cristalización | objeto formal, hilo, forma matemática |
| Q5 | 2 | Operación | codificación, orden, comando, programación imperativa |
| Q6 | 2 | Declaración | descripción declarativa, regla, hilo en lugar de comando |
| Q7 | 2 | Delegación | delegar, referenciar, transferir responsabilidad |
| Q8 | 2 | Biblioteca | piedra reutilizable, panal, mineral, colección de bloques |
| Q9 | 2 | Framework | marco, estructura orgánica, estructura de inteligencia general |
| Q10 | 3 | Restricción | limitación, estructura, cuerda, espacio de posibilidades |
| Q11 | 3 | Interfaz | intervención, interfaz, inserción de pensamiento |
| Q12 | 3 | Caja de herramientas | métodos, matemáticas, álgebra, análisis, topología, teoría de categorías |
| Q13 | 3 | Programa | servicio, paradigma, enfoque de pensamiento |
| Q14 | 3 | Orquestación | composición, coreografía, dirección, maestría |
| Q15 | 3 | Aplicación | aplicación, obra, opus |
| Q16 | 3 | Operación | menú, kernel, sistema operativo, ejecución |
| Q17 | 4 | Compresión | compresión; operación inversa: descompresión |
| Q18 | 4 | Arquitectura | construcción, plano, forma total portante |
| Q19 | 4 | Generación | generación; movimiento inverso: degeneración o decadencia |
| Q20 | 4 | Módulo/Máquina | desarrollo terminado, dispositivo, patrón, máquina de dificultad |

Las cuatro capas de valor:

```text
Valor 1: Q1–Q4     monedas básicas
Valor 2: Q5–Q9     monedas operativas
Valor 3: Q10–Q16   monedas sistémicas
Valor 4: Q17–Q20   monedas de capital
```

---

## 4. Suma, riqueza y cartera

Las monedas pueden sumarse. Primero se suma el valor de línea.

Ejemplo:

```text
2 × Q1
1 × Q8
3 × Q10
1 × Q20
```

Valor nominal:

```text
2 × 1 VL = 2 VL
1 × 2 VL = 2 VL
3 × 3 VL = 9 VL
1 × 4 VL = 4 VL
Valor total = 17 VL
```

En octadegramos:

```text
17 VL × 18 = 306 octadegramos
```

Cartera:

```text
Wallet = (Q1:2, Q8:1, Q10:3, Q20:1)
Valor = 17 VL
```

Regla clave: el mismo valor nominal no significa la misma función semántica.

```text
4 × Q1 = 4 VL
1 × Q20 = 4 VL
pero: 4 × Q1 ≠ 1 × Q20
```

Cuatro núcleos de tarea todavía no son una máquina terminada. Una máquina terminada puede descomponerse en núcleos de tarea, pero no es idéntica a ellos.

---

## 5. Deudas y operaciones inversas

Las deudas son saldos negativos de monedas.

```text
-1 × Q18 = debo una unidad de arquitectura
```

Una cuenta puede ser nominalmente positiva y semánticamente peligrosa:

```text
+3 × Q5 -1 × Q10
```

Nominalmente:

```text
3 × Q5 = 6 VL
-1 × Q10 = -3 VL
Neto = +3 VL
```

Pero semánticamente falta Q10: faltan estructura y restricción.

> Un actor puede ser nominalmente rico y semánticamente ilíquido.

La deuda y la operación inversa son distintas:

```text
-Q17  = deuda de compresión
1/Q17 = descompresión
-Q19  = deuda de generación
1/Q19 = degeneración
```

Cuatro tipos de deuda:

| Tipo de deuda | Significado | Ejemplo |
|---|---|---|
| Deuda de valor | se debe solo una cantidad de valor | 10 VL |
| Deuda de altura | se debe una clase de valor | tres monedas de altura 2 |
| Deuda de tipo | se debe un tipo específico de moneda | 2 × Q10 |
| Deuda de proyecto | se debe una prestación concreta | servicio Q13 con interfaz Q11 |

---

## 6. Cuentas, balance y riqueza

Una cuenta no es un único saldo, sino un vector de 20 tipos de monedas.

```text
Cuenta A:
Q1:  10
Q2:   5
Q3:   2
Q5:   8
Q6:  -1
Q8:   3
Q9:   1
Q10: -2
Q20:  1
```

Los valores negativos son deudas. La cuenta se lee de dos formas:

```text
Lectura nominal = suma de todos los saldos × valor de línea
Balance semántico = excedentes y carencias por tipo de moneda
```

Tres formas de riqueza:

1. **Riqueza nominal:** valor total en VL.
2. **Riqueza semántica:** posesión de los tipos de moneda correctos para actuar realmente.
3. **Riqueza líquida:** capacidad de pagar deudas vencidas con el tipo correcto de moneda.

Una empresa con mucho Q5 y Q13 posee mucho código y muchos servicios. Si debe Q10, Q16 y Q18, tiene deuda estructural, operativa y arquitectónica.

---

## 7. Mercados

La Q-economía necesita varios mercados.

### Mercado de monedas

Las monedas Q se intercambian entre sí:

```text
1 × Q20 por 4 × Q1
1 × Q18 por 2 × Q5
1 × Q13 por 1 × Q10
```

Un intercambio puede estar equilibrado nominalmente y desequilibrado semánticamente.

### Mercado laboral

Humanos o agentes venden trabajo:

```text
Trabajo Q5: codificar
Trabajo Q6: especificar
Trabajo Q10: restricciones y estructura
Trabajo Q11: interfaces
Trabajo Q18: arquitectura
Trabajo Q20: construcción de módulos
```

### Mercado de bienes

Los productos y servicios tienen una firma Q. Ejemplo:

```text
Servicio de análisis:
Q10: 2
Q11: 1
Q12: 1
Q13: 2
Q16: 1
```

### Mercado de crédito

Aquí se comercian créditos y deudas.

```text
A debe a B 5 × Q18.
B vende el crédito a C.
C paga menos que el valor nominal por el riesgo de impago.
```

### Mercado de futuros

Se comercian entregas futuras.

```text
Entrega en 30 días: 3 × Q13 + 1 × Q16
Precio hoy: 12 VL
```

### Mercado de seguros

Los seguros cubren fallos de tipos de moneda concretos, sobre todo Q16, Q18 y Q20.

### Mercado de bienes comunes

Q8, Q9, Q12 y Q16 suelen ser bienes comunes. Bibliotecas, frameworks, herramientas e infraestructura necesitan financiación pública o colectiva parcial.

---

## 8. Precios y tipos de cambio

Existe un precio nominal y un precio de mercado.

```text
Precio nominal(Qi) = valor de línea h(Qi)
```

El precio de mercado surge de escasez, calidad, urgencia y confianza:

```text
Precio de mercado(Qi) =
Valor nominal(Qi)
× escasez
× factor de calidad
× factor de urgencia
× factor de confianza
```

Ejemplo:

```text
Q18 nominal = 4 VL
escasez: ×1.5
calidad: ×1.2
urgencia: ×1.3
confianza: ×1.1
precio de mercado = 4 × 1.5 × 1.2 × 1.3 × 1.1 = 10.296 VL
```

En las deudas de tipo, el mismo valor nominal no basta. Quien debe Q18 no puede pagar automáticamente con Q17. El acreedor puede fijar una quita semántica:

```text
1 × Q17 cuenta como sustituto del 60% de 1 × Q18
```

Esto es un **haircut semántico**.

---

## 9. Producción y recetas de producción

Producción significa transformar dificultad en formas estructuradas, ejecutables y reutilizables.

Cadena principal de valor:

```text
Q1 tarea
→ Q2 descomposición
→ Q3 abstracción
→ Q4 forma formal
→ Q5/Q6 programación o especificación
→ Q8/Q9 reutilización y marco
→ Q10/Q11 estructura e interfaz
→ Q13 servicio
→ Q15 aplicación
→ Q18 arquitectura
→ Q20 máquina/módulo
```

Recetas de producción:

```text
Salida Q5 codificación:
Q1 tarea + Q3 modelo + tiempo de trabajo

Salida Q6 especificación:
Q1 tarea + Q3 abstracción + Q10 restricción

Salida Q8 biblioteca:
varios Q5 + al menos un Q6 + competencia de herramientas Q12 + compresión Q17

Salida Q9 framework:
bibliotecas Q8 + restricciones Q10 + interfaces Q11 + lógica de servicio Q13

Salida Q13 servicio:
código Q5 + especificación Q6 + restricciones Q10 + interfaz Q11 + biblioteca Q8

Salida Q18 arquitectura:
restricciones Q10 + interfaces Q11 + orquestación Q14 + compresión Q17 + forma Q3/Q4

Salida Q20 módulo/máquina:
programa Q13 + aplicación Q15 + operación Q16 + arquitectura Q18 + generación Q19
```

---

## 10. Creación monetaria y casa de moneda

Las monedas nuevas no se crean arbitrariamente. Se acuñan cuando una prestación ha sido verificada y reconocida.

```text
arquitectura validada → nuevas monedas Q18
servicio validado → nuevas monedas Q13
módulo validado → nuevas monedas Q20
```

La casa de moneda tiene cinco tareas:

```text
1. acuñar monedas
2. destruir monedas
3. clasificar tipos de moneda
4. impedir falsificaciones
5. asegurar estabilidad de precios
```

La moneda no está respaldada por oro, sino por **trabajo semántico verificado**.

Los validadores revisan el trabajo:

```text
Validador Q5 revisa código.
Validador Q6 revisa especificaciones.
Validador Q10 revisa restricciones.
Validador Q18 revisa arquitectura.
Validador Q20 revisa madurez de módulo.
```

La validación falsa genera pérdida de reputación y deudas de penalización.

---

## 11. Bancos, crédito e intereses

Los bancos conceden crédito, pero no crean automáticamente valor real. El crédito crea capacidad de pago; el respaldo surge solo mediante trabajo productivo.

Ejemplo:

```text
Banco presta a la empresa F:
3 × Q18
2 × Q13

Empresa F recibe:
+3 Q18 +2 Q13

Al mismo tiempo surge:
-3 Q18 -2 Q13 más intereses
```

El interés surge de tiempo, riesgo, escasez y dificultad semántica:

```text
Interés(Qi) =
tasa base
+ riesgo de impago
+ recargo de escasez
+ recargo de complejidad
- descuento por garantía
```

Las monedas altas como Q18 y Q20 suelen tener intereses mayores porque su fallo puede dañar sistemas enteros.

---

## 12. Deuda técnica como deuda real

La deuda técnica se contabiliza como deuda Q real.

| Deuda | Significado |
|---|---|
| -Q1 | tarea básica no resuelta |
| -Q2 | problema no descompuesto |
| -Q3 | modelo ausente |
| -Q4 | precisión formal ausente |
| -Q5 | implementación ausente |
| -Q6 | especificación ausente |
| -Q7 | responsabilidad no aclarada |
| -Q8 | biblioteca o reutilización ausente |
| -Q9 | marco ausente |
| -Q10 | restricciones ausentes |
| -Q11 | interfaz rota |
| -Q12 | herramienta ausente |
| -Q13 | servicio ausente |
| -Q14 | deuda de coordinación |
| -Q15 | aplicación no entregada |
| -Q16 | deuda operativa o de runtime |
| -Q17 | complejidad no comprimida |
| -Q18 | deuda arquitectónica |
| -Q19 | capacidad generativa ausente |
| -Q20 | módulo ausente o máquina inacabada |

Un proyecto con mucho Q5 pero Q10 y Q18 negativos parece productivo, pero está enfermo estructuralmente.

```text
+20 Q5
-10 Q10
-5 Q18
```

Eso significa: mucho código, mala estructura, mala arquitectura.

---

## 13. Actores, división del trabajo y capacidades

Los actores son hogares, empresas, bancos, validadores, Estado, fondos de bienes comunes y socios de comercio exterior.

Las capacidades se describen como perfil Q:

```text
Agente A:
Q1: 0.8
Q2: 0.7
Q3: 0.5
Q5: 0.9
Q6: 0.4
Q10: 0.3
Q18: 0.1
```

Esto significa: fuerte en reconocer y codificar, débil en estructura y arquitectura.

Las profesiones surgen según los tipos de moneda:

```text
Analista Q1/Q2: encuentra y descompone problemas
Teórico Q3/Q4: modela y formaliza
Programador Q5: implementa
Especificador Q6: describe declarativamente
Coordinador Q7: delega y referencia
Bibliotecario Q8: construye componentes reutilizables
Constructor de frameworks Q9: crea marcos
Ingeniero de restricciones Q10: fija límites y estructura
Diseñador de interfaces Q11: conecta sistemas
Toolsmith Q12: construye herramientas
Constructor de servicios Q13: crea servicios
Orquestador Q14: compone procesos
Constructor de aplicaciones Q15: crea obras utilizables
Ingeniero de operación Q16: mantiene la ejecución estable
Compresor Q17: condensa complejidad
Arquitecto Q18: construye formas portantes
Constructor de generadores Q19: crea sistemas generativos
Constructor de módulos Q20: entrega máquinas terminadas
```

---

## 14. Estado, impuestos y bienes comunes

El Estado protege la moneda, estabiliza crisis y financia bienes comunes. Los impuestos pueden cobrarse en VL:

```text
impuesto sobre la renta: porcentaje del valor nominal
impuesto sobre transacciones: pequeña tasa sobre operaciones de mercado
gravamen de deuda: recargo sobre apalancamiento arriesgado Q18/Q20
```

El gasto público apoya especialmente:

```text
Q8 bibliotecas
Q9 frameworks
Q12 herramientas
Q16 infraestructura
educación
validación
seguridad pública
```

Las reglas antimonopolio son importantes porque Q8, Q9, Q16, Q18 y Q20 pueden controlar las condiciones de producción. Los medios incluyen interfaces abiertas, obligación de interoperabilidad, licencias obligatorias, contribuciones a bienes comunes y, si es necesario, división de empresas.

---

## 15. Inflación, deflación y crisis

La inflación aquí no significa solo subida de precios. Significa multiplicar un tipo de moneda sin respaldo semántico suficiente.

```text
Inflación Q5  = mucho código sin especificación, restricciones y arquitectura
Inflación Q13 = muchos servicios sin fiabilidad
Inflación Q18 = arquitectura declarada sin construcción portante
Inflación Q20 = módulos inacabados vendidos como máquinas
```

La deflación significa: hay muy pocas monedas válidas para las tareas existentes. Ejemplo: muchas tareas Q1, pero poco Q5, Q10 y Q18.

Crisis típica:

```text
Q5:  muy alto
Q13: alto
Q15: alto
Q10: bajo
Q16: bajo
Q18: bajo
```

Esto significa: mucho código y muchas aplicaciones, pero poca estructura, operación y arquitectura. La crisis aparece como fallos, problemas de integración, brechas de seguridad y deuda de mantenimiento.

La política de crisis no debe imprimir dinero a ciegas. Debe fortalecer los tipos de moneda que faltan.

---

## 16. Calidad, reputación y propiedad

No todas las monedas del mismo tipo tienen la misma calidad. Clases de calidad:

```text
A = verificado, estable, reutilizable
B = utilizable, pero limitado
C = experimental
D = problemático
F = inválido o fallido
```

Q18-A vale más que Q18-C, aunque ambas valen nominalmente 4 VL.

La reputación se registra por tipo de moneda:

```text
Agente A:
reputación Q5: 90
reputación Q6: 60
reputación Q10: 45
reputación Q18: 20
```

La propiedad existe sobre monedas, artefactos y derechos de uso:

```text
propiedad de monedas: 5 × Q10
propiedad de artefactos: programa, biblioteca, máquina
derecho de uso: licencia sobre Q8, Q9 o Q20
```

---

## 17. Economía de licencias y comercio de tareas

Las bibliotecas Q8, frameworks Q9, servicios Q13, aplicaciones Q15 y módulos Q20 pueden licenciarse.

Ejemplo:

```text
Biblioteca Q8:
uso único: 1 VL
uso comercial: 2 Q5 por mes
licencia open commons: financiación pública
```

Las tareas también pueden comerciarse. Q1 es materia prima: una buena tarea, pregunta de investigación o necesidad de cliente puede comprarse y venderse. Una buena tarea es valiosa porque puede convertirse en base de una cadena Q1→Q20.

---

## 18. Cadena de valor Q1 → Q20 e inteligencia

El movimiento económico central:

```text
Q1 → Q20
tarea → máquina
```

Cadena completa:

```text
Q1  reconocer tarea
Q2  descomponer tarea
Q3  formar modelo
Q4  formalizar
Q5  implementar
Q6  declarar
Q7  delegar
Q8  construir biblioteca
Q9  crear framework
Q10 fijar restricciones
Q11 construir interfaces
Q12 proporcionar herramientas
Q13 crear servicio
Q14 orquestar servicios
Q15 construir aplicación
Q16 asegurar operación
Q17 comprimir complejidad
Q18 construir arquitectura
Q19 permitir generación
Q20 entregar módulo/máquina
```

La inteligencia es capacidad de transformación:

```text
Inteligencia = capacidad de transformar Q1 en formas Q superiores
```

Transformación baja:

```text
Q1 → Q5 = la tarea se convierte en código
```

Transformación alta:

```text
Q1 → Q18 → Q19 → Q20 = la tarea se estructura arquitectónicamente, se vuelve generativa y se entrega como máquina
```

---

## 19. Bolsa, índice de precios, masa monetaria e insolvencia

En la bolsa Q, las monedas tienen precios de mercado. Ejemplo:

| Moneda | Nominal | Precio de mercado |
|---:|---:|---:|
| Q1 | 1 | 0.8 |
| Q5 | 2 | 2.4 |
| Q8 | 2 | 3.1 |
| Q10 | 3 | 5.0 |
| Q13 | 3 | 3.6 |
| Q18 | 4 | 9.5 |
| Q20 | 4 | 7.8 |

El índice de precios Q mide un ciclo típico de desarrollo:

```text
4 × Q1
2 × Q5
2 × Q8
2 × Q10
1 × Q13
1 × Q16
1 × Q18
1 × Q20
```

La masa monetaria se mide por tipo de moneda:

```text
M(Q18) = cantidad de monedas Q18 válidas
L(Q18) = deuda abierta en Q18
```

Peligroso:

```text
L(Q18) muy alto
M(Q18) bajo
```

Esto es una crisis de deuda arquitectónica.

La insolvencia puede ser nominal o semántica. La insolvencia nominal significa que las deudas totales superan los activos totales. La insolvencia semántica significa que el valor total alcanza, pero faltan los tipos correctos de moneda.

---

## 20. Investigación, comercio exterior y continuo R

La investigación crea sobre todo:

```text
Q1 nuevas tareas
Q3 nuevas abstracciones
Q4 nuevos objetos formales
Q12 nuevas herramientas
Q17 compresiones
Q19 principios generativos
```

El comercio exterior conecta la Q-economía con otras economías. Se exportan especialmente Q8, Q9, Q13, Q15, Q18 y Q20. Se importan materias primas, hardware, energía, datos, trabajo y capital.

El continuo R es la ejecución real o la realidad práctica. El valor Q se vuelve especialmente fuerte cuando pasa a efecto R:

```text
Q18 arquitectura + Q20 módulo → máquina real → valor R
Q13 servicio + Q16 operación → servicio en funcionamiento → utilidad R
```

---

## 21. Ledger triple-store, contratos y simulación

La contabilidad se realiza como ledger semántico de triples:

```text
(sujeto, predicado, objeto)
```

Ejemplos:

```text
(Agente A, posee, 3 × Q10)
(Agente A, debe, 1 × Q18 a Agente B)
(Proyecto P, requiere, 2 × Q5)
(Proyecto P, produce, 1 × Q13)
(Q17, operación inversa, descompresión)
```

Un contrato contiene:

```text
partes
objeto de entrega
firma Q
precio
vencimiento
grado de calidad
sanción
validación
```

La simulación avanza por periodos:

```text
1. Surgen tareas.
2. Los actores eligen acciones.
3. Los mercados abren.
4. Ocurre la producción.
5. Los resultados se validan.
6. Las monedas se acuñan o rechazan.
7. Los pagos se contabilizan.
8. Las deudas se actualizan.
9. Los precios se ajustan.
10. La reputación se actualiza.
11. El Estado y la casa de moneda reaccionan.
```

---

## 22. Leyes de la Q-economía

```text
1. Ley de la moneda: cada moneda Q tiene número, valor de línea y significado.
2. Ley de suma: los valores de monedas se suman por altura de fila.
3. Ley semántica: igual valor nominal no significa igual función.
4. Ley de deuda: los saldos negativos de monedas son deudas.
5. Ley de inversión: 1/Qi es operación inversa, -Qi es deuda.
6. Ley de producción: la producción transforma dificultad Q1 en formas Q superiores.
7. Ley de validación: nuevas monedas surgen solo de desempeño verificado.
8. Ley de precio: precios de mercado surgen de nominal, escasez, calidad, riesgo y confianza.
9. Ley de solvencia: la salud requiere solvencia nominal y semántica.
10. Ley de estabilidad: las monedas altas deben estar respaldadas por estructura, operación y arquitectura.
```

---

## 23. Definición final

La Q-economía es un orden monetario, crediticio y productivo semántico.

Su moneda consiste en Q1 hasta Q20. El valor de cada moneda es su altura de fila. Las monedas pueden sumarse, intercambiarse, prestarse y deberse. Las deudas son saldos Q negativos. Las operaciones inversas se escriben como 1/Qi y no son deudas.

La producción es la transformación de dificultad en formas estructuradas, ejecutables y reutilizables. La riqueza surge cuando tareas Q1 se convierten en efecto real mediante código Q5, estructura Q10, servicios Q13, arquitectura Q18 y módulos Q20.

Las crisis surgen cuando la riqueza nominal y la solvencia semántica se separan. La estabilidad surge mediante validación, interfaces abiertas, buena arquitectura, deudas visibles y bienes comunes públicos.

**Frase central:** Esta economía no paga simplemente trabajo. Paga la transformación lograda de dificultad en inteligencia funcional.
