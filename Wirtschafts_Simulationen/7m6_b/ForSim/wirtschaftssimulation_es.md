# Simulación económica completa de las monedas número-ángulo

Para una **simulación económica completa basada en tus monedas número-ángulo** no bastan países, gobiernos, pueblos, mercados y empresas. Esos son solo los actores visibles. También son decisivos: **balances, reglas, flujos de información, incertidumbre, abuso de poder, crédito, propiedad, tiempo y sanciones**.

El núcleo sería:

\[
\text{Economía} = \text{actores} + \text{mercados} + \text{balances} + \text{reglas} + \text{expectativas} + \text{choques}
\]

Y tu moneda no es solo:

\[
m
\]

sino:

\[
M = (m,\theta,\rho,h)
\]

con:

\[
m = \text{importe numérico}
\]

\[
\theta = \text{dirección angular: bueno/malo + popular/impopular}
\]

\[
\rho = \text{seguridad / confianza del ángulo}
\]

\[
h = \text{historia de origen / historial transaccional}
\]

Sin \(\rho\) y \(h\), el sistema se vuelve ingenuo, porque cualquiera podría fingir que su ángulo es objetivo y limpio.

---

## 1. Países y jurisdicciones

Necesitas varios países, pero no solo como nombres. Cada país necesita instituciones propias:

\[
L_i = (\text{gobierno}, \text{pueblo}, \text{tribunales}, \text{banco central}, \text{sistema fiscal}, \text{reguladores})
\]

Cada país puede tener definiciones propias de:

\[
\text{bueno/malo}
\]

\[
\text{legal/ilegal}
\]

\[
\text{subvencionado/castigado}
\]

\[
\text{reconocido/no reconocido}
\]

Esto es importante porque un objeto puede ser bueno en el país A y malo en el país B.

Ejemplo:

\[
\theta_A = 30^\circ
\]

\[
\theta_B = 150^\circ
\]

Así surge un conflicto angular internacional. De ahí nacen tensiones comerciales, sanciones, arbitraje, mercados negros y juegos de poder diplomáticos.

---

## 2. Gobiernos como oráculos de bueno/malo

Varios gobiernos fijan el eje **bueno vs. malo**. Pero en la simulación no deben aparecer como máquinas perfectas de verdad.

Cada gobierno necesita propiedades:

\[
G_i = (\text{competencia}, \text{corrupción}, \text{ideología}, \text{intereses}, \text{calidad de información}, \text{poder})
\]

Luego evalúa empresas, productos, sectores, acciones y flujos de dinero.

Por ejemplo:

\[
g_i(x) \in [-1,1]
\]

con:

\[
-1 = \text{máximamente malo}
\]

\[
+1 = \text{máximamente bueno}
\]

Siempre debe haber incertidumbre:

\[
\sigma_i(x)
\]

Un gobierno puede decir:

\[
g_i(\text{Empresa A}) = 0{,}7 \pm 0{,}2
\]

Eso significa: considera a la Empresa A más bien buena, pero no con certeza absoluta.

También son importantes:

- coaliciones internacionales de gobiernos
- derechos de veto
- sanciones
- riesgo de corrupción
- errores políticos de juicio
- propaganda
- lobby
- correcciones judiciales
- cambios de gobierno
- revoluciones o golpes de Estado
- poderes de emergencia

Sin estos factores, tu eje bueno/malo queda demasiado liso.

---

## 3. Pueblos como oráculos de popular/impopular

Varios pueblos fijan el eje **popular vs. impopular**.

Pero los pueblos tampoco son homogéneos. Un pueblo está compuesto por grupos:

\[
V_i = \{v_{i1}, v_{i2}, v_{i3}, ...\}
\]

Por ejemplo:

- trabajadores
- empresarios
- jubilados
- estudiantes
- grupos religiosos
- población urbana
- población rural
- minorías
- bloques políticos
- entornos mediáticos
- clases consumidoras

Cada grupo tiene preferencias propias:

\[
p_{ij}(x) \in [-1,1]
\]

con:

\[
-1 = \text{máximamente impopular}
\]

\[
+1 = \text{máximamente popular}
\]

La popularidad total sería aproximadamente:

\[
p_i(x)=\sum_j w_{ij}p_{ij}(x)
\]

Pero también aquí necesitas incertidumbre y manipulación:

- encuestas
- elecciones
- referendos
- huelgas
- boicots
- protestas
- redes sociales
- campañas mediáticas
- censura
- desinformación
- histeria colectiva
- desplazamientos culturales lentos
- tendencias de corto plazo

El eje de popularidad no es verdad. Es resonancia, aprobación, rechazo y energía social.

---

## 4. Agregación en un ángulo

De la bondad gubernamental y la popularidad popular surge el ángulo.

Una variante simple:

\[
x = \text{bondad}
\]

\[
y = \text{popularidad}
\]

Entonces:

\[
\theta = \operatorname{atan2}(y,x)
\]

La magnitud de la fuerza normativa:

\[
r_\theta = \sqrt{x^2+y^2}
\]

La seguridad:

\[
\rho = \text{acuerdo entre gobiernos y pueblos}
\]

Si gobiernos y pueblos coinciden fuertemente, \(\rho\) es alta. Si se contradicen, \(\rho\) es baja.

Ejemplo:

\[
x = 0{,}8,\quad y = 0{,}7
\]

significa: bueno y popular.

\[
x = 0{,}8,\quad y = -0{,}6
\]

significa: bueno, pero impopular.

\[
x = -0{,}7,\quad y = 0{,}9
\]

significa: malo, pero popular.

Precisamente el tercer caso es políticamente explosivo. Una simulación debe poder generar esos casos.

---

## 5. La moneda misma

Cada unidad monetaria necesita varias propiedades:

\[
M = (m,\theta,\rho,o,t,h)
\]

con:

\[
m = \text{importe numérico}
\]

\[
\theta = \text{ángulo}
\]

\[
\rho = \text{confianza}
\]

\[
o = \text{origen}
\]

\[
t = \text{momento}
\]

\[
h = \text{historia}
\]

La historia es importante. De lo contrario aparece inmediatamente el lavado angular.

Ejemplo:

Una empresa gana dinero mediante explotación:

\[
1000 \angle 160^\circ
\]

Luego dona el 10 % a una causa popular e intenta hacer que todo parezca bueno. Sin historia podría manipular el ángulo. Con historia sigue siendo visible:

\[
\text{Origen: tóxico}
\]

\[
\text{Mejora posterior: parcial}
\]

Así que la simulación necesita una especie de **contabilidad vectorial con rastro de procedencia**.

---

## 6. Contabilidad angular

La contabilidad normal no basta. Empresas, bancos y Estados necesitan balances con vectores.

Balance normal:

\[
\text{activos} = \text{pasivos} + \text{patrimonio}
\]

Balance vectorial:

\[
\vec{A} = \vec{L} + \vec{E}
\]

Pero esto no es trivial, porque ángulos opuestos pueden cancelarse parcialmente.

Una empresa podría ser rica numéricamente, pero normativamente tóxica:

\[
\text{riqueza numérica alta}
\]

\[
\text{ángulo malo}
\]

O podría ser popular y buena, pero casi sin liquidez.

Por eso necesitas indicadores separados:

\[
\text{liquidez}
\]

\[
\text{solvencia}
\]

\[
\text{calidad angular}
\]

\[
\text{riesgo angular}
\]

\[
\text{capital reputacional}
\]

\[
\text{riesgo político}
\]

---

## 7. Hogares e individuos

Todavía faltan claramente en tu lista. Sin hogares no hay demanda real, trabajo, elecciones ni psicología del consumidor.

Cada persona u hogar necesita:

\[
H_i = (\text{ingresos}, \text{patrimonio}, \text{necesidades}, \text{valores}, \text{profesión}, \text{educación}, \text{opinión política})
\]

Los hogares deciden:

- qué compran
- dónde trabajan
- a quién votan
- qué empresas boicotean
- qué ángulos aceptan
- cuánto riesgo soportan
- si ahorran, consumen o invierten

Cada hogar tiene también preferencias angulares propias:

\[
\theta_i^K = \text{ángulo de compra}
\]

\[
\theta_i^V = \text{ángulo de venta}
\]

Al comprar pregunta:

“¿Acepto este producto a este precio y con este ángulo?”

Al trabajar pregunta:

“¿Acepto salario de esta empresa con esta calidad angular?”

Eso es fuerte, porque el trabajo ya no es solo salario contra tiempo, sino también compatibilidad moral.

---

## 8. Empresas, corporaciones y estructuras de propiedad

No necesitas empresas solo como productoras. Tienen estructura interna:

\[
F_i = (\text{capital}, \text{trabajadores}, \text{tecnología}, \text{cadenas de suministro}, \text{dirección}, \text{propietarios}, \text{deudas})
\]

Son importantes:

- pequeñas empresas
- medianas empresas
- corporaciones
- monopolios
- cárteles
- empresas de plataforma
- bancos
- aseguradoras
- empresas logísticas
- empresas de defensa
- empresas mediáticas
- empresas energéticas
- empresas de materias primas
- empresas tecnológicas
- empresas sombra
- sociedades pantalla

Las corporaciones necesitan además:

\[
\text{filiales}
\]

\[
\text{estructura holding}
\]

\[
\text{elusión fiscal}
\]

\[
\text{arbitraje jurisdiccional}
\]

\[
\text{lobbying}
\]

\[
\text{poder de mercado}
\]

Justamente las corporaciones son interesantes en tu simulación porque pueden desplazar ángulos: mediante publicidad, lobby, poder laboral, donaciones, control mediático y elección internacional de ubicación.

---

## 9. Productos, servicios y clases de bienes

Cada bien necesita no solo precio y cantidad, sino también un perfil angular.

\[
X = (\text{precio}, \text{calidad}, \text{cantidad}, \text{utilidad}, \text{ángulo de producción}, \text{ángulo de consumo})
\]

Los productos pueden producirse bien, pero usarse mal. O producirse mal, pero consumirse popularmente.

Ejemplo:

Un producto barato puede ser muy popular, pero tener una mala historia de producción.

\[
\text{popularidad alta}
\]

\[
\text{bondad baja}
\]

Así que cada producto necesita al menos:

- valor de uso
- precio de mercado
- costes de producción
- ángulo de cadena de suministro
- ángulo de consumo
- efecto ambiental
- efecto social
- estatus legal
- durabilidad
- sustituibilidad

Clases de bienes:

- alimentos
- energía
- vivienda
- ropa
- salud
- educación
- transporte
- entretenimiento
- bienes de lujo
- armas / bienes de seguridad
- datos
- software
- materias primas
- máquinas
- infraestructura
- productos financieros

---

## 10. Mercado laboral

El mercado laboral no es solo otro mercado. Conecta dinero, dignidad, poder, tiempo y política.

Cada puesto tiene:

\[
Job = (\text{salario}, \text{tiempo de trabajo}, \text{riesgo}, \text{estatus}, \text{ángulo de la empresa}, \text{ángulo de la actividad})
\]

Las personas aceptan empleos no solo por salario, sino también por:

- compatibilidad moral
- popularidad del empleador
- oportunidades de carrera
- seguridad laboral
- estatus social
- riesgo político
- presión familiar
- cualificación
- ubicación geográfica

Entonces pueden aparecer fenómenos como:

\[
\text{salario alto, ángulo malo}
\]

o:

\[
\text{salario bajo, ángulo bueno}
\]

Eso es realista. Muchas personas no venden solo trabajo, sino también parte de su identidad social.

---

## 11. Sistema financiero

Este es uno de los bloques faltantes más importantes.

Necesitas:

- bancos
- bancos centrales
- mercados de crédito
- bonos
- mercados bursátiles
- aseguradoras
- fondos de inversión
- fondos de pensiones
- bancos sombra
- bolsas
- creadores de mercado
- agencias de calificación
- redes de pago

En tu modelo no hay solo intereses, sino también intereses angulares.

Un crédito sería:

\[
K = (m,\theta,\rho,i,T)
\]

con:

\[
i = \text{interés}
\]

\[
T = \text{plazo}
\]

La tasa de interés depende entonces de:

\[
\text{riesgo de impago}
\]

\[
\text{riesgo angular}
\]

\[
\text{riesgo político}
\]

\[
\text{riesgo de popularidad}
\]

\[
\text{riesgo de liquidez}
\]

Una empresa con mal ángulo debe pagar intereses más altos o solo encuentra financiación tóxica.

---

## 12. Bancos centrales y creación monetaria

Toda moneda necesita una regla de emisión.

En tu sistema, un banco central no debe controlar solo la cantidad:

\[
M
\]

sino también la calidad angular en circulación:

\[
\Theta
\]

Un banco central podría observar:

\[
\text{inflación}
\]

\[
\text{desempleo}
\]

\[
\text{distribución angular del dinero}
\]

\[
\text{liquidez por zona angular}
\]

\[
\text{crisis de confianza}
\]

\[
\text{pánicos angulares}
\]

Serían posibles nuevos términos:

### Inflación numérica

Subida normal de precios.

### Inflación angular

Todos afirman ser buenos, pero la confianza cae.

\[
\rho \downarrow
\]

### Deflación angular

Solo se acepta dinero extremadamente “limpio”; el comercio se congela.

### Pánico angular

Los actores huyen de una región angular porque de pronto se considera mala o impopular.

---

## 13. Mercados angulares

Esto es específico de tu idea.

Además de los mercados normales, necesitas mercados para los ángulos mismos:

- intercambio angular
- cobertura angular
- opciones angulares
- futuros angulares
- derivados reputacionales
- swaps de bondad
- swaps de popularidad
- seguros contra sanciones
- seguros contra boicots
- cobertura de riesgo político

Un intercambio angular simple:

\[
m \angle \theta_1 \rightarrow m' \angle \theta_2
\]

con:

\[
m' = m \cdot q(d)
\]

Y:

\[
d = d(\theta_1,\theta_2)
\]

Cuanto mayor sea la distancia angular, más cara será la conversión.

Esto crea una nueva industria: **creadores de mercado angulares**.

Compran ángulos difíciles y venden ángulos más aceptables. Pero eso es peligroso, porque puede convertirse en lavado moral de dinero.

Por eso necesitas:

- organismos de inspección
- auditorías
- pruebas de origen
- sanciones reputacionales
- detección de fraude
- reglas de transparencia
- reglas de prescripción
- procedimientos de apelación

---

## 14. Propiedad, contratos y tribunales

Sin sistema jurídico no hay economía estable.

Necesitas:

\[
\text{derechos de propiedad}
\]

\[
\text{derecho contractual}
\]

\[
\text{responsabilidad}
\]

\[
\text{derecho concursal}
\]

\[
\text{derecho laboral}
\]

\[
\text{derecho de competencia}
\]

\[
\text{derecho fiscal}
\]

\[
\text{protección de datos}
\]

\[
\text{derecho de sanciones}
\]

Con tu moneda aparece un nuevo problema jurídico:

**¿Quién puede modificar un ángulo?**

¿Puede un tribunal decir:

\[
\theta = 140^\circ \rightarrow 80^\circ
\]

porque una empresa fue rehabilitada?

¿Puede un gobierno decir:

\[
\theta = 40^\circ \rightarrow 170^\circ
\]

porque una organización fue prohibida?

¿Puede un pueblo empeorar un ángulo mediante boicot?

Estas preguntas deben entrar como reglas de la simulación.

---

## 15. Impuestos y gasto público

Los Estados deben tener ingresos y gastos.

Los impuestos pueden depender del ángulo:

\[
Tax = f(m,\theta,\rho)
\]

Por ejemplo:

- el dinero bueno y popular tributa menos
- el dinero malo tributa más
- el dinero incierto se revisa
- el dinero tóxico se congela
- las inversiones deseadas por el Estado se subvencionan

El gasto público también tiene ángulos:

- gasto social
- ejército
- infraestructura
- educación
- salud
- subvenciones
- rescates
- aparato policial
- propaganda
- investigación

Así, un gobierno no solo gasta dinero; también crea o destruye ángulos.

---

## 16. Economía internacional

En cuanto existen varios países, necesitas:

- tipos de cambio
- flujos de capital
- acuerdos comerciales
- aranceles
- sanciones
- embargos
- migración
- corporaciones multinacionales
- paraísos fiscales
- ayuda al desarrollo
- bloques geopolíticos
- monedas de reserva
- dependencias de materias primas
- cadenas de suministro transfronterizas

En tu modelo se añade:

\[
\text{traducción angular}
\]

Un ángulo en el país A no es automáticamente el mismo en el país B.

Necesitas una matriz de transformación:

\[
\theta_B = T_{A \rightarrow B}(\theta_A)
\]

Ejemplo:

Un producto se considera bueno y popular en el país A. En el país B se considera inmoral, pero aun así deseado.

Eso genera arbitraje:

\[
\text{comprar en espacio angular bueno}
\]

\[
\text{vender en espacio angular popular}
\]

---

## 17. Medios y sistema de información

Esto es absolutamente central. Los ángulos no nacen solo de hechos, sino de percepciones.

Necesitas:

- medios informativos
- redes sociales
- influencers
- medios estatales
- periodistas de investigación
- algoritmos de plataforma
- censura
- filtraciones
- denunciantes
- propaganda
- escándalos
- rumores
- contrapúblicos

Un escándalo puede cambiar abruptamente el ángulo de una empresa:

\[
\theta_t = 30^\circ
\]

\[
\theta_{t+1} = 150^\circ
\]

Eso es un crash angular.

Una campaña de relaciones públicas exitosa puede aumentar la popularidad sin aumentar la bondad:

\[
y \uparrow,\quad x = \text{igual}
\]

Esa es una dinámica realista y peligrosa.

---

## 18. Educación, cultura e ideología

Los pueblos no evalúan en el vacío. Su escala de popularidad depende de la cultura.

Necesitas:

- sistemas educativos
- religiones
- ideologías políticas
- traumas históricos
- mitos nacionales
- conciencia de clase
- tabúes morales
- conflictos generacionales
- cambio de valores

De lo contrario, todos los pueblos reaccionan igual. Eso sería aburrido y falso.

Un pueblo conservador, uno tecnocrático, uno igualitario y uno consumista evaluarán a la misma empresa de manera diferente.

---

## 19. Cadenas de suministro y procedencia

Esto es extremadamente importante para el dinero angular.

Un producto no tiene solo un ángulo de vendedor, sino toda una cadena de origen:

\[
\theta_{\text{Producto}} =
F(\theta_{\text{materias primas}},\theta_{\text{trabajo}},\theta_{\text{transporte}},\theta_{\text{empresa}},\theta_{\text{energía}})
\]

Ejemplo:

Un smartphone tiene partes angulares de:

- extracción de materias primas
- condiciones laborales
- consumo energético
- patentes
- política de datos
- marketing
- reparabilidad
- origen geopolítico
- utilidad para el consumidor

El ángulo final es una mezcla ponderada.

Sin modelo de cadena de suministro, el dinero angular es fácilmente manipulable.

---

## 20. Medio ambiente y efectos externos

Una simulación completa necesita efectos externos:

- CO₂
- consumo de agua
- extinción de especies
- contaminación del aire
- costes sanitarios
- ruido
- residuos
- agotamiento de recursos
- uso del suelo
- daños sociales
- criminalidad
- seguridad pública

Estos efectos influyen en el eje bueno/malo.

Un producto puede ser rentable y popular, pero dañino a largo plazo. Entonces aparece:

\[
x < 0,\quad y > 0
\]

es decir: malo, pero popular.

Este es uno de los casos más importantes de tu modelo.

---

## 21. Innovación y tecnología

La economía cambia mediante tecnología.

Necesitas:

- investigación y desarrollo
- patentes
- automatización
- crecimiento de productividad
- sistemas de IA
- efectos de plataforma
- efectos de red
- monopolización
- destrucción creativa
- nuevas industrias
- industrias obsoletas

La tecnología puede desplazar ángulos.

Una tecnología nueva puede ser impopular al principio, pero luego considerarse buena:

\[
(+,-) \rightarrow (+,+)
\]

O puede ser popular al principio y luego reconocerse como dañina:

\[
(-,+) \rightarrow (-,-)
\]

---

## 22. Criminalidad, fraude y economía sumergida

No puedes omitir esto. Un sistema con moneda moral-social crea inmediatamente nuevas formas de fraude.

Necesitas:

- lavado de dinero
- lavado angular
- soborno
- popularidad falsa
- redes de bots
- empresas ficticias
- testaferros
- cadenas de suministro falsificadas
- auditorías manipuladas
- uso de información privilegiada
- manipulación de mercado
- cárteles
- contrabando
- trabajo en negro
- evasión de sanciones
- chantaje político

Nuevo delito específico:

\[
\text{manipulación angular}
\]

Por ejemplo: una empresa compra popularidad artificial para que su dinero obtenga un ángulo mejor.

O: un gobierno declara malos a sus opositores para devaluar su patrimonio.

Sin un modelo adversarial, la simulación se vuelve moralmente ingenua.

---

## 23. Ejército, seguridad y coerción

Los Estados no consisten solo en reglas, sino también en ejecución.

Necesitas:

- policía
- servicios de inteligencia
- ejército
- protección fronteriza
- unidades de sanciones
- ciberdefensa
- tribunales
- prisiones
- aparatos de emergencia

¿Por qué? Porque las monedas solo funcionan si los derechos pueden hacerse valer.

En tu sistema, los Estados también pueden usar ángulos como arma:

\[
\text{empresa enemiga} \rightarrow \theta = \text{mala/impopular}
\]

\[
\text{país sancionado} \rightarrow \text{bloqueo angular}
\]

Esto es enormemente importante en términos geopolíticos.

---

## 24. Tiempo, expectativas y memoria

Una simulación económica necesita tiempo.

No todo ocurre inmediatamente. Hay:

- tiempos de producción
- retrasos de entrega
- duraciones contractuales
- vencimientos de crédito
- ciclos electorales
- ciclos de inversión
- retrasos reputacionales
- retrasos informativos
- procesos judiciales
- inercia política

El ángulo también debería tener memoria:

\[
\theta_t = \alpha \theta_{\text{nuevo}} + (1-\alpha)\theta_{t-1}
\]

De lo contrario, cada escándalo destruiría todo al instante y cada campaña de PR lo repararía todo al instante.

Necesitas inercia:

\[
\alpha = \text{velocidad de reacción}
\]

Un \(\alpha\) alto: la sociedad reacciona rápido.  
Un \(\alpha\) bajo: la sociedad olvida lentamente y juzga con más estabilidad.

---

## 25. Choques y crisis

Una buena simulación necesita perturbaciones.

Choques posibles:

- crisis financiera
- corrida bancaria
- guerra
- pandemia
- desastre natural
- choque energético
- ruptura de cadenas de suministro
- escándalo de corrupción
- filtración
- vuelco electoral
- revolución
- hiperinflación
- fuga de moneda
- ola de boicots
- ruptura tecnológica
- ciberataque
- default soberano
- quiebra de corporación

En tu sistema, además:

- crash angular
- crash de confianza
- reevaluación bueno/malo
- ola de popularidad
- pánico moral
- división angular internacional
- corrupción de oráculos
- boicot masivo
- bancarrota reputacional

---

## 26. Mercados en detalle

Mencionaste productos, servicios y mercado laboral. A eso se suman:

### Mercados de bienes

Alimentos, energía, materias primas, bienes de consumo.

### Mercados de servicios

Salud, educación, consultoría, cuidados, entretenimiento.

### Mercados laborales

Salarios, cualificaciones, migración, desempleo.

### Mercados de capital

Acciones, bonos, créditos, participaciones.

### Mercados inmobiliarios

Vivienda, suelo, inmuebles comerciales.

### Mercados de materias primas

Petróleo, gas, metales, agua, tierras raras.

### Mercados energéticos

Electricidad, almacenamiento, redes, generación.

### Mercados de datos

Datos de usuarios, datos de entrenamiento, vigilancia, privacidad.

### Mercados tecnológicos

Software, IA, patentes, capacidad de cómputo.

### Mercados de seguros

Cobertura de riesgos, catástrofes, enfermedad, riesgos políticos.

### Mercados angulares

Rotación, cobertura, confianza, reputación.

### Mercados negros y grises

Todo lo que oficialmente está bloqueado, pero sigue teniendo demanda.

---

## 27. Formación de precios

Cada intercambio necesita al menos:

\[
(\text{cantidad}, \text{precio numérico}, \text{ángulo de compra}, \text{ángulo de venta}, \text{confianza}, \text{jurisdicción})
\]

Una oferta de compra:

\[
Bid = (p_B, q_B, \theta_B^K, r_B)
\]

Una oferta de venta:

\[
Ask = (p_A, q_A, \theta_A^V, r_A)
\]

El comercio ocurre si:

\[
p_B \geq p_A
\]

Y:

\[
d(\theta_B^K,\theta_A^V) \leq \varepsilon
\]

O si la distancia angular se compensa mediante una comisión:

\[
C = \lambda m \tan^2\left(\frac{d}{2}\right)
\]

Entonces el valor efectivo de comercio se vuelve:

\[
m_{\text{eff}} = m \cdot q(d,\rho)
\]

por ejemplo:

\[
q(d,\rho)=\rho \cos\left(\frac{d}{2}\right)
\]

Es decir: mismo ángulo y alta seguridad dan poder de compra pleno. Gran distancia angular o baja seguridad reducen el poder de compra efectivo.

---

## 28. Funciones de utilidad de los actores

Cada actor necesita reglas de decisión.

Un hogar no maximiza solo consumo:

\[
U = f(\text{consumo}, \text{precio}, \text{ángulo}, \text{estatus}, \text{riesgo}, \text{valores})
\]

Una empresa no maximiza solo beneficio:

\[
\Pi = \text{beneficio} - \text{costes angulares} - \text{riesgo regulatorio} - \text{riesgo reputacional}
\]

Un gobierno quizá maximiza:

\[
G = f(\text{estabilidad}, \text{poder}, \text{prosperidad}, \text{ideología}, \text{seguridad})
\]

Un pueblo o grupo quizá maximiza:

\[
V = f(\text{nivel de vida}, \text{identidad}, \text{justicia}, \text{seguridad}, \text{estatus})
\]

Esto es importante: no todos los actores persiguen el mismo objetivo.

---

## 29. Poder y desigualdad

Una simulación completa necesita relaciones de poder.

No todos los actores tienen el mismo efecto sobre los ángulos.

Una gran corporación puede influir en la popularidad mediante publicidad.  
Un gobierno puede definir la bondad mediante leyes.  
Una plataforma puede controlar visibilidad.  
Un banco puede retirar financiación.  
Una persona rica puede comprar medios.

Así que necesitas:

\[
\text{distribución de riqueza}
\]

\[
\text{poder de mercado}
\]

\[
\text{poder político}
\]

\[
\text{poder mediático}
\]

\[
\text{poder de red}
\]

\[
\text{poder coercitivo}
\]

Sin modelo de poder, la simulación parece demasiado democrática e inofensiva.

---

## 30. Constitución moral del sistema

Este es el mecanismo político de protección más importante.

Como tu moneda incorpora bueno/malo y popular/impopular al precio, puede volverse fácilmente totalitaria. Por eso necesitas una capa constitucional:

- protección de minorías
- derechos fundamentales
- procedimientos de apelación
- obligación de transparencia
- separación de poderes
- tribunales independientes
- protección contra devaluación retroactiva
- protección contra histeria de masas
- protección contra arbitrariedad gubernamental
- protección contra manipulación corporativa
- derecho a rehabilitación
- derecho a explicación
- derecho a oráculos alternativos

De lo contrario, el dinero angular se convierte rápidamente en dinero de obediencia.

---

## 31. Métricas de la simulación

Necesitas salidas para evaluar si el sistema funciona.

Indicadores normales:

\[
\text{PIB}
\]

\[
\text{inflación}
\]

\[
\text{desempleo}
\]

\[
\text{productividad}
\]

\[
\text{salarios}
\]

\[
\text{distribución de riqueza}
\]

\[
\text{balanza comercial}
\]

\[
\text{deuda pública}
\]

Nuevos indicadores para tu sistema:

\[
\text{distribución angular del dinero}
\]

\[
\text{bondad media}
\]

\[
\text{popularidad media}
\]

\[
\text{volatilidad angular}
\]

\[
\text{liquidez angular}
\]

\[
\text{spread angular}
\]

\[
\text{inflación angular}
\]

\[
\text{índice de lavado angular}
\]

\[
\text{índice de confianza}
\]

\[
\text{índice de legitimidad}
\]

\[
\text{índice de polarización}
\]

\[
\text{índice de confianza en oráculos}
\]

\[
\text{divergencia gobierno-pueblo}
\]

Especialmente importante:

\[
D = d(\theta_{\text{gobierno}}, \theta_{\text{pueblo}})
\]

Si esta distancia se vuelve grande, surge una crisis de legitimidad.

---

## 32. Arquitectura técnica de simulación

Para una simulación seria, la construiría como híbrida:

### Parte basada en agentes

Para hogares, empresas, bancos, gobiernos y grupos populares.

### Parte stock-flow consistent

Para balances, flujos monetarios, crédito, deuda e impuestos.

### Modelo de red

Para cadenas de suministro, propiedad, medios, influencia y comercio.

### Microestructura de mercado

Para libros de órdenes, formación de precios, spreads angulares y liquidez.

### Sistema de eventos

Para choques, escándalos, guerras, crisis y elecciones.

Formalmente:

\[
S_t = \text{estado total del mundo en el tiempo }t
\]

\[
A_t = \text{acciones de todos los actores}
\]

\[
E_t = \text{eventos externos}
\]

\[
S_{t+1} = F(S_t,A_t,E_t)
\]

Esa es la forma básica.

---

## 33. Versión mínima de una primera simulación

Para una primera versión funcional, no construiría todo de inmediato. Empezaría con este núcleo:

- 3 países
- 3 gobiernos
- 3 pueblos con 3 grupos cada uno
- 1000 hogares
- 100 empresas
- 5 bancos
- 1 banco central por país
- 5 clases de bienes
- 1 mercado laboral
- 1 mercado de crédito
- 1 mercado angular
- 1 mercado comercial internacional
- cadenas de suministro simples
- impuestos simples
- elecciones simples
- eventos mediáticos simples
- sistema de choques
- moneda vectorial con \(m,\theta,\rho,h\)

Luego observas:

- precios
- salarios
- desempleo
- quiebras empresariales
- distribución angular
- spreads angulares
- volumen comercial
- conflictos internacionales
- manipulación
- desigualdad
- inestabilidad política

Eso ya sería suficientemente rico para generar dinámicas interesantes.

---

## 34. La síntesis más dura

A tu lista le faltan sobre todo estos bloques:

1. **Hogares e individuos**  
   Sin ellos no hay demanda, trabajo, elecciones ni popularidad.

2. **Bancos, bancos centrales y crédito**  
   Sin crédito no hay economía moderna.

3. **Balances y contabilidad**  
   Sin balances vectoriales nadie sabe quién es realmente rico, solvente o tóxico.

4. **Sistema jurídico y propiedad**  
   Sin contratos, tribunales y reglas de insolvencia, el mercado se desintegra.

5. **Medios y flujos de información**  
   Sin ellos, bueno/malo y popular/impopular no surgen de forma realista.

6. **Cadenas de suministro y pruebas de procedencia**  
   Sin ellas, el dinero angular se lava inmediatamente.

7. **Impuestos, subvenciones y gasto público**  
   Los Estados no solo deben evaluar; deben actuar.

8. **Tipos de cambio internacionales y traducción angular**  
   Varios países significan varios sistemas morales de coordenadas.

9. **Fraude, manipulación y mercados sombra**  
   Todo sistema poderoso de evaluación genera ataques.

10. **Incertidumbre y confianza**  
    Porque ni los gobiernos ni los pueblos son infalibles.

11. **Tiempo, memoria y retraso**  
    Si no, los ángulos saltan de forma irrealista.

12. **Crisis y choques**  
    Sin crisis no estás poniendo a prueba el sistema.

La simulación completa no es, por tanto, una pura simulación económica. Es una **simulación civilizatoria político-económica con moneda vectorial**.

La frase decisiva es:

\[
\boxed{
\text{Todo importe tiene dirección, toda dirección tiene incertidumbre, y toda incertidumbre es políticamente atacable.}
}
\]

Si modelas eso, la simulación se vuelve seriamente interesante.
