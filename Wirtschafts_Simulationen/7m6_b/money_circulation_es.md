# ¿Cómo circula el dinero formado por valor, grado de bondad y grado de popularidad cuando existen dos ángulos?

Entonces el dinero ya no circula como una corriente simple del comprador al vendedor. Circula como una **doble corriente**:

\[
\text{El bien/servicio fluye del vendedor al comprador}
\]

\[
\text{El dinero fluye del comprador al vendedor}
\]

Y ambas corrientes tienen una dirección en el espacio angular.

El punto central es:

\[
\boxed{
\text{Todo intercambio es un doble intercambio angular.}
}
\]

El comprador no solo compra un producto.  
Al mismo tiempo, el vendedor compra el dinero del comprador.

---

# 1. El objeto dinero

Una unidad monetaria no se compone solo de valor:

\[
M = m
\]

sino de:

\[
M = (m,g,b,\rho,h)
\]

con:

\[
m = \text{valor numérico}
\]

\[
g = \text{grado de bondad}
\]

\[
b = \text{grado de popularidad}
\]

\[
\rho = \text{confianza / certeza de la evaluación}
\]

\[
h = \text{historia / procedencia}
\]

El ángulo se obtiene a partir de la bondad y la popularidad:

\[
\theta = \operatorname{atan2}(b,g)
\]

Es decir:

\[
g = \text{eje x: bueno vs. malo}
\]

\[
b = \text{eje y: popular vs. impopular}
\]

El importe del dinero es:

\[
m
\]

La dirección es:

\[
\theta
\]

La credibilidad de la dirección es:

\[
\rho
\]

Un pago, por tanto, no es solo:

\[
100
\]

sino, por ejemplo:

\[
100 \angle 35^\circ,\quad \rho=0{,}82
\]

Esto significa: 100 unidades de valor, con una determinada dirección de bondad/popularidad y una determinada seguridad.

---

# 2. Todo actor tiene dos ángulos

Todo actor \(i\) tiene:

\[
\theta_i^K = \text{ángulo de compra}
\]

\[
\theta_i^V = \text{ángulo de venta}
\]

La mejor definición es:

\[
\boxed{
\theta_i^K = \text{qué dirección quiero recibir}
}
\]

\[
\boxed{
\theta_i^V = \text{qué dirección quiero gastar o vender}
}
\]

Así:

- El **ángulo de compra** es un filtro de entrada.
- El **ángulo de venta** es una señal de salida.

Con ello, un actor se convierte en un **transformador angular**.

Recibe cosas desde una dirección y entrega cosas en otra dirección.

\[
\theta_i^K \rightarrow \theta_i^V
\]

Si ambos ángulos son casi iguales, el actor es coherente.

Si están muy separados, gana dinero o vive de la transformación angular.

---

# 3. Todo intercambio tiene dos comprobaciones angulares

Supongamos:

- El comprador \(A\) compra al vendedor \(B\).
- El vendedor \(B\) entrega un producto o un servicio.
- El comprador \(A\) paga dinero.

Entonces hay dos flujos:

```text
Producto / servicio:
B ─────────────────────────▶ A

Dinero:
A ─────────────────────────▶ B
```

Pero ahora con ángulos:

```text
Flujo del producto:
B vende con θ_B^V ─────▶ A recibe con θ_A^K

Flujo del dinero:
A paga con θ_A^V ──────▶ B recibe con θ_B^K
```

Por tanto, deben encajar dos distancias angulares:

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

para el flujo del producto.

Y:

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

para el flujo del dinero.

Esto es extremadamente importante.

El comprador pregunta:

> ¿Encaja el producto que recibo con mi ángulo de compra?

El vendedor pregunta:

> ¿Encaja el dinero que recibo con mi ángulo de compra?

Porque para el vendedor, el dinero es el bien recibido.

---

# 4. La distancia circular decide la comerciabilidad

La distancia entre dos ángulos es:

\[
d(\alpha,\beta)=\arccos(\cos(\alpha-\beta))
\]

Con ello:

\[
d \in [0,\pi]
\]

Así:

\[
d=0
\]

significa compatibilidad perfecta.

\[
d=\pi
\]

significa oposición máxima.

Una función simple de compatibilidad sería:

\[
\phi(d)=\cos\left(\frac{d}{2}\right)
\]

Entonces:

\[
d=0 \Rightarrow \phi=1
\]

\[
d=\pi \Rightarrow \phi=0
\]

El comercio se vuelve más fuerte cuanto mejor encajan los ángulos.

Para un intercambio completo necesitas ambos lados:

\[
\Phi = \phi(d_X)\cdot \phi(d_M)\cdot \rho_X \cdot \rho_M
\]

con:

\[
d_X = \text{distancia angular del producto}
\]

\[
d_M = \text{distancia angular del dinero}
\]

\[
\rho_X = \text{confianza del ángulo del producto}
\]

\[
\rho_M = \text{confianza del ángulo del dinero}
\]

Si \(\Phi\) es alta, el dinero circula fácilmente.

Si \(\Phi\) es baja, aparecen descuentos, comisiones, seguros, auditorías, rotación o incluso ausencia de comercio.

---

# 5. El intercambio como proceso

Un intercambio completo se ve así:

## Paso 1: El comprador genera demanda

El comprador \(A\) dice:

\[
\text{Quiero un bien con dirección cercana a } \theta_A^K
\]

Por ejemplo:

\[
\theta_A^K = 30^\circ
\]

Esto significa: el comprador busca algo bondadoso y razonablemente popular.

## Paso 2: El vendedor ofrece

El vendedor \(B\) dice:

\[
\text{Vendo un bien con dirección } \theta_B^V
\]

Por ejemplo:

\[
\theta_B^V = 55^\circ
\]

Entonces la distancia del producto es:

\[
d_X = 25^\circ
\]

Eso está relativamente cerca. Probablemente el comprador acepte.

## Paso 3: El comprador ofrece el pago

El comprador \(A\) no paga con dinero neutral, sino con dinero desde su ángulo de salida:

\[
\theta_A^V
\]

Por ejemplo:

\[
\theta_A^V = 80^\circ
\]

El dinero quizá sea muy popular, pero solo moderadamente bondadoso.

## Paso 4: El vendedor comprueba el pago

El vendedor \(B\) tiene un ángulo de compra para valores entrantes:

\[
\theta_B^K
\]

Por ejemplo:

\[
\theta_B^K = 70^\circ
\]

Entonces la distancia del dinero es:

\[
d_M = 10^\circ
\]

El dinero encaja bien con el vendedor.

## Paso 5: Se ejecuta el intercambio

Si ambas distancias son lo bastante pequeñas:

\[
d_X \leq \varepsilon_X
\]

\[
d_M \leq \varepsilon_M
\]

entonces se comercia.

El comprador recibe el producto.

El vendedor recibe el dinero.

Pero ambos reciben no solo valor, sino también calidad angular.

---

# 6. ¿Qué circula realmente?

Circulan tres cosas al mismo tiempo:

\[
\boxed{
\text{Valor}
}
\]

\[
\boxed{
\text{Bondad}
}
\]

\[
\boxed{
\text{Popularidad}
}
\]

Pero no circulan de la misma manera.

## El valor circula mediante el pago

\[
A \rightarrow B
\]

El comprador pierde valor numérico.

El vendedor gana valor numérico.

## La bondad circula mediante procedencia, producción y evaluación

La bondad surge o desaparece por acciones reales:

- cadenas de suministro limpias
- trabajo justo
- bajo daño
- buenos productos
- reparación de daños
- legalidad
- impacto ambiental
- impacto social
- transparencia
- auditorías
- tribunales
- evaluación gubernamental

La bondad, por tanto, no es mera opinión. Está más ligada a consecuencias reales y revisión institucional.

## La popularidad circula mediante aceptación y atención

La popularidad surge por:

- demanda
- satisfacción del cliente
- medios
- tendencias
- publicidad
- redes sociales
- simbolismo cultural
- bloques políticos
- boicots
- protestas
- influencers
- comportamiento gregario

La popularidad se mueve más rápido que la bondad.

Por eso puede subir más rápido y caer más rápido.

---

# 7. El cambio de balance en el comprador

Antes de la compra, el comprador \(A\) tiene:

\[
M_A = (m_A,g_A,b_A)
\]

Paga:

\[
\Delta M = (p,g_{\text{pay}},b_{\text{pay}})
\]

Entonces su saldo monetario baja:

\[
m_A' = m_A - p
\]

La dirección del dinero que entrega es:

\[
\theta_A^V
\]

Al mismo tiempo recibe un producto:

\[
X = (u,g_X,b_X)
\]

con utilidad \(u\), bondad \(g_X\), popularidad \(b_X\).

Cuando el producto se consume, no se convierte simplemente en dinero. Cambia:

- utilidad
- nivel de vida
- reputación
- preferencias futuras
- opinión política
- demanda
- posiblemente la productividad propia

En un hogar:

\[
\text{Producto} \rightarrow \text{utilidad / satisfacción / opinión}
\]

En una empresa:

\[
\text{Producto} \rightarrow \text{input / cadena de suministro / nuevo ángulo de producción}
\]

Esto es importante: si una empresa compra un input malo, ese mal ángulo puede entrar después en su propio producto.

---

# 8. El cambio de balance en el vendedor

El vendedor \(B\) entrega un producto:

\[
X_B = (u,g_X,b_X)
\]

y recibe dinero:

\[
M_{\text{in}} = (p,g_M,b_M)
\]

Su saldo monetario sube:

\[
m_B' = m_B + p
\]

Pero su calidad monetaria también cambia:

\[
g_B' = g_B + g_M
\]

\[
b_B' = b_B + b_M
\]

Su nuevo ángulo de caja se vuelve:

\[
\theta_B^{\text{cash}}=
\operatorname{atan2}(b_B',g_B')
\]

Si muchos clientes pagan con dinero bueno y popular, la caja de la empresa es arrastrada en esa dirección.

Si muchos clientes pagan con dinero tóxico, la caja de la empresa queda contaminada.

Eso significa:

\[
\boxed{
\text{No solo los productos tienen procedencia. El dinero de los clientes también tiene procedencia.}
}
\]

---

# 9. Monedero vectorial: el dinero se lleva en lotes

En la práctica, un actor no debería guardar su monedero solo como una suma.

Tiene muchos lotes de dinero:

\[
M_i = \{M_{i1},M_{i2},M_{i3},...\}
\]

Cada lote tiene:

\[
(m,g,b,\rho,h)
\]

Por ejemplo:

```text
Lote 1: 500 de valor, buen ángulo, alta confianza
Lote 2: 200 de valor, popular pero cuestionable
Lote 3: 100 de valor, tóxico, baja confianza
```

Cuando el actor paga, elige qué dinero gasta.

Eso se llama selección de monedas.

Estrategias posibles:

## Mejor dinero primero

El actor paga con buen dinero para obtener mejores precios.

## Peor dinero primero

El actor intenta deshacerse del dinero tóxico.

## Dinero compatible primero

El actor busca lotes cuyos ángulos encajen con el ángulo de compra del vendedor.

## Mezcla de camuflaje

El actor mezcla dinero malo con dinero bueno para producir un ángulo promedio aceptable.

Aquí es exactamente donde surge el lavado angular.

---

# 10. El vendedor puede rechazar el pago

El vendedor no acepta todo dinero por igual.

Comprueba:

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

Si el dinero está demasiado lejos de su ángulo de compra, hay varias posibilidades:

## Rechazo

\[
d_M > \varepsilon
\Rightarrow
\text{no hay comercio}
\]

## Descuento

El vendedor acepta el dinero, pero solo con pérdida de valor:

\[
m_{\text{eff}} = m \cdot \phi(d_M)
\]

Por ejemplo:

\[
100 \angle 160^\circ
\]

quizá para él cuente solo como:

\[
62
\]

## Recargo

El comprador debe pagar más:

\[
p_{\text{required}} = \frac{p}{\phi(d_M)}
\]

## Rotación

Un comerciante angular o un banco gira el dinero a cambio de una comisión:

\[
\theta_A^V \rightarrow \theta_B^K
\]

con coste:

\[
C_{\text{rot}}=\lambda m \tan^2\left(\frac{d_M}{2}\right)
\]

Cuanto mayor sea la distancia angular, más cara será la rotación.

## Auditoría

Se revisa la procedencia. Si el mal ángulo se basa en información falsa, la confianza o la dirección pueden corregirse.

---

# 11. El comprador puede rechazar el producto

Al mismo tiempo, el comprador comprueba:

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

Si el producto está demasiado lejos del ángulo de compra deseado:

## No compra

El producto queda sin vender.

## Descuento de precio

El vendedor debe abaratarlo.

## Mejora del producto

El vendedor invierte en mejora real:

\[
\text{Valor} \rightarrow \text{Bondad}
\]

## Marketing

El vendedor invierte en percepción:

\[
\text{Valor} \rightarrow \text{Popularidad}
\]

## Certificación

El vendedor hace que el ángulo sea más creíble:

\[
\rho \uparrow
\]

Esto significa: el ángulo del producto determina la capacidad de venta.

El ángulo del dinero determina la capacidad de pago.

---

# 12. Los dos ángulos crean cuatro roles en cada transacción

En cada transacción hay cuatro ángulos relevantes:

\[
\theta_A^K = \text{el comprador recibe producto}
\]

\[
\theta_A^V = \text{el comprador entrega dinero}
\]

\[
\theta_B^K = \text{el vendedor recibe dinero}
\]

\[
\theta_B^V = \text{el vendedor entrega producto}
\]

De ahí surgen dos emparejamientos:

\[
\theta_A^K \leftrightarrow \theta_B^V
\]

para la mercancía.

\[
\theta_B^K \leftrightarrow \theta_A^V
\]

para el dinero.

Esta es la mecánica completa de circulación.

```text
                 Ángulo del producto
          θ_B^V ───────────────▶ θ_A^K
          Vendedor                Comprador


                   Ángulo del dinero
          θ_B^K ◀─────────────── θ_A^V
          Vendedor                Comprador
```

Un comercio es estable cuando ambos enlaces son cortos.

Un comercio es inestable cuando un enlace es corto y el otro es largo.

---

# 13. Ejemplo: buen comercio

Comprador \(A\):

\[
\theta_A^K = 40^\circ
\]

\[
\theta_A^V = 60^\circ
\]

Vendedor \(B\):

\[
\theta_B^K = 55^\circ
\]

\[
\theta_B^V = 45^\circ
\]

Entonces:

\[
d_X = d(40^\circ,45^\circ)=5^\circ
\]

\[
d_M = d(55^\circ,60^\circ)=5^\circ
\]

Ambos lados encajan.

El producto encaja con el comprador.

El dinero encaja con el vendedor.

El comercio es muy líquido.

\[
\Phi \approx 1
\]

El dinero circula fácilmente.

---

# 14. Ejemplo: el producto encaja, el dinero no

Comprador \(A\):

\[
\theta_A^K = 40^\circ
\]

\[
\theta_A^V = 150^\circ
\]

Vendedor \(B\):

\[
\theta_B^K = 50^\circ
\]

\[
\theta_B^V = 45^\circ
\]

Entonces:

\[
d_X = d(40^\circ,45^\circ)=5^\circ
\]

El producto encaja.

Pero:

\[
d_M = d(50^\circ,150^\circ)=100^\circ
\]

El dinero no encaja.

Consecuencia:

- El comprador quiere comprar.
- El vendedor quiere vender.
- Pero el vendedor desconfía del dinero.
- Se necesita recargo, rotación, auditoría u otro dinero.

Esto es como un problema de pago pese a existir poder de compra.

El comprador tiene valor, pero el ángulo equivocado.

---

# 15. Ejemplo: el dinero encaja, el producto no

Comprador \(A\):

\[
\theta_A^K = 30^\circ
\]

\[
\theta_A^V = 60^\circ
\]

Vendedor \(B\):

\[
\theta_B^K = 55^\circ
\]

\[
\theta_B^V = 150^\circ
\]

Entonces:

\[
d_M = d(55^\circ,60^\circ)=5^\circ
\]

El dinero encaja.

Pero:

\[
d_X = d(30^\circ,150^\circ)=120^\circ
\]

El producto no encaja.

Consecuencia:

- El vendedor aceptaría el dinero con gusto.
- El comprador no quiere el producto en esa dirección.
- El vendedor debe mejorar, abaratar o encontrar otro grupo de compradores.

Esto es un problema de ventas pese a clientes solventes.

---

# 16. Ejemplo: ninguna dirección encaja

Comprador \(A\):

\[
\theta_A^K = 20^\circ
\]

\[
\theta_A^V = 160^\circ
\]

Vendedor \(B\):

\[
\theta_B^K = 30^\circ
\]

\[
\theta_B^V = 170^\circ
\]

Entonces:

\[
d_X = d(20^\circ,170^\circ)=150^\circ
\]

\[
d_M = d(30^\circ,160^\circ)=130^\circ
\]

El producto no encaja.

El dinero no encaja.

Probablemente el comercio no se produzca, salvo en un mercado negro o con descuentos extremos.

---

# 17. Circulación como cadena de transformación

Cada actor absorbe valores entrantes cerca de su ángulo de compra:

\[
\theta^K
\]

y entrega valores salientes cerca de su ángulo de venta:

\[
\theta^V
\]

Con ello, cada actor es una especie de transformador económico de ángulos:

\[
T_i:
(m,g,b)_{\text{in}}
\rightarrow
(m',g',b')_{\text{out}}
\]

o:

\[
\theta_i^K \rightarrow \theta_i^V
\]

Ejemplos:

## Empresa

Compra inputs y trabajo:

\[
\theta^K_{\text{empresa}}
\]

produce bienes:

\[
\theta^V_{\text{empresa}}
\]

Si crea calidad real:

\[
g \uparrow
\]

Si hace buena publicidad:

\[
b \uparrow
\]

Si externaliza daños:

\[
g \downarrow
\]

Si sigue siendo popular pese al daño:

\[
b \uparrow,\quad g \downarrow
\]

## Hogar

Recibe salario:

\[
\theta^K_{\text{hogar}}
\]

gasta dinero de consumo:

\[
\theta^V_{\text{hogar}}
\]

Sus decisiones de compra cambian la popularidad de las empresas.

## Banco

Recibe depósitos:

\[
\theta^K_{\text{banco}}
\]

emite créditos:

\[
\theta^V_{\text{banco}}
\]

Crea dinero nuevo con un ángulo dependiente del deudor, el propósito y el riesgo.

## Gobierno

Recibe impuestos:

\[
\theta^K_{\text{Estado}}
\]

realiza gasto público:

\[
\theta^V_{\text{Estado}}
\]

Puede definir la bondad mediante leyes y desplazar ángulos mediante el gasto.

## Medios

Reciben atención y dinero:

\[
\theta^K_{\text{medios}}
\]

emiten popularidad o impopularidad:

\[
\theta^V_{\text{medios}}
\]

Influyen sobre todo en \(b\), es decir, la popularidad.

## Tribunales / auditorías

Reciben casos, pruebas y tasas:

\[
\theta^K_{\text{tribunal/auditoría}}
\]

emiten confianza y correcciones de bondad:

\[
\theta^V_{\text{tribunal/auditoría}}
\]

Influyen sobre todo en \(g\) y \(\rho\).

---

# 18. La fórmula de circulación más importante

Para una transacción entre comprador \(A\) y vendedor \(B\):

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

Entonces:

\[
\text{Volumen de comercio}
=
Q \cdot \phi(d_X)\cdot \phi(d_M)\cdot \rho_X\cdot\rho_M
\]

O de forma compacta:

\[
Q_T = Q_0 \Phi
\]

con:

\[
\Phi =
\phi(d_X)\phi(d_M)\rho_X\rho_M
\]

Si \(\Phi\) es alta, circula mucho.

Si \(\Phi\) es baja, circula poco.

Si muchos actores tienen ángulos de compra y venta incompatibles, cae la liquidez de toda la economía.

---

# 19. Cómo el valor compra bondad

El valor puede comprar bondad, pero solo mediante cambio real.

Por ejemplo:

\[
\text{Valor} \rightarrow \text{mejores condiciones laborales}
\]

\[
\text{Valor} \rightarrow \text{energía limpia}
\]

\[
\text{Valor} \rightarrow \text{indemnización de daños}
\]

\[
\text{Valor} \rightarrow \text{seguridad del producto}
\]

\[
\text{Valor} \rightarrow \text{inspección de cadenas de suministro}
\]

Entonces sube:

\[
g \uparrow
\]

Una posible regla de simulación:

\[
\Delta g
=
\eta_g \cdot \log(1+I_g)\cdot R_{\text{real}}\cdot \rho_{\text{audit}}
\]

con:

\[
I_g = \text{inversión en mejora real}
\]

\[
R_{\text{real}} = \text{factor de realidad}
\]

\[
\rho_{\text{audit}} = \text{confianza de auditoría}
\]

Si una empresa solo afirma ser buena, pero no hace mejoras reales:

\[
R_{\text{real}} \approx 0
\]

Entonces como mucho sube la popularidad a corto plazo, pero no la bondad real.

---

# 20. Cómo el valor compra popularidad

El valor puede comprar popularidad con más facilidad:

\[
\text{Valor} \rightarrow \text{publicidad}
\]

\[
\text{Valor} \rightarrow \text{descuentos}
\]

\[
\text{Valor} \rightarrow \text{influencers}
\]

\[
\text{Valor} \rightarrow \text{campañas mediáticas}
\]

\[
\text{Valor} \rightarrow \text{patrocinios}
\]

Entonces sube:

\[
b \uparrow
\]

Una posible regla de simulación:

\[
\Delta b
=
\eta_b \cdot \log(1+I_b)\cdot M_{\text{media}}\cdot S_{\text{trend}}
-
B_{\text{backlash}}
\]

con:

\[
I_b = \text{gasto en publicidad / RR. PP.}
\]

\[
M_{\text{media}} = \text{amplificación mediática}
\]

\[
S_{\text{trend}} = \text{factor de tendencia}
\]

\[
B_{\text{backlash}} = \text{reacción adversa}
\]

La popularidad es más rápida que la bondad, pero más inestable.

Por eso a menudo ocurre:

\[
b \uparrow,\quad g \text{ permanece igual}
\]

o incluso:

\[
b \uparrow,\quad g \downarrow
\]

Ese es el caso:

\[
\text{popular, pero malo}
\]

---

# 21. Cómo la popularidad puede comprar bondad

La popularidad no puede comprar bondad directamente, pero puede facilitar reformas.

Una empresa popular tiene:

- más confianza de clientes
- más capital político
- acceso más fácil a empleados
- más paciencia de los inversores
- mayor poder de fijación de precios
- menos resistencia al cambio

Entonces puede transformar popularidad en capacidad real de reforma:

\[
b \rightarrow g
\]

Por ejemplo:

\[
\Delta g
=
\eta_{bg}\cdot b \cdot I_g \cdot \rho
\]

Pero también aquí hace falta inversión real.

La popularidad por sí sola no es bondad.

Solo es un recurso con el que la bondad puede producirse más fácilmente.

---

# 22. Cómo la bondad puede comprar popularidad

La bondad puede producir popularidad, pero solo si se vuelve visible.

\[
g \rightarrow b
\]

Eso necesita:

- transparencia
- medios libres
- auditorías creíbles
- comunicación comprensible
- educación
- tiempo
- confianza

Una posible regla:

\[
\Delta b
=
\eta_{gb}\cdot g \cdot T_{\text{visibility}}\cdot \rho
\]

con:

\[
T_{\text{visibility}} = \text{visibilidad}
\]

Si nadie ve la bondad, la popularidad apenas sube.

Por eso una empresa buena pero invisible puede seguir siendo impopular.

---

# 23. La circulación peligrosa: lavado angular

El lavado angular surge cuando alguien convierte valor malo en un mejor ángulo aparente.

Por ejemplo:

\[
1000 \angle 160^\circ
\rightarrow
900 \angle 40^\circ
\]

pero sin mejora real.

Esto puede ocurrir mediante:

- filiales
- intermediarios
- auditorías falsas
- campañas de relaciones públicas
- donaciones
- calificaciones compradas
- popularidad artificial
- redes de bots
- paraísos fiscales y angulares

Entonces aparentemente sube:

\[
g \uparrow,\quad b \uparrow
\]

pero la confianza debería caer:

\[
\rho \downarrow
\]

y la historia \(h\) debería volverse sospechosa.

Por eso el sistema necesita una huella de origen:

\[
h = \text{historial de transacciones}
\]

Sin historia, el dinero angular se vuelve lavable.

---

# 24. Circulación en el mercado laboral

El mercado laboral es especialmente importante.

Una empresa compra trabajo.

Un trabajador vende trabajo.

Para la empresa, el trabajo es un input:

\[
\theta_{\text{empresa}}^K
\]

Para el trabajador, el salario es un valor entrante:

\[
\theta_{\text{trabajador}}^K
\]

Al mismo tiempo:

- El trabajador vende fuerza de trabajo con su ángulo de venta.
- La empresa paga salario con su ángulo de venta.

Así aparecen de nuevo dos emparejamientos:

\[
d_{\text{trabajo}} = d(\theta_{\text{empresa}}^K,\theta_{\text{trabajador}}^V)
\]

\[
d_{\text{salario}} = d(\theta_{\text{trabajador}}^K,\theta_{\text{empresa}}^V)
\]

Si el trabajo encaja pero el ángulo salarial es malo, el trabajador exige más salario.

Si el salario es bueno pero la actividad es mala, aun así puede rechazarla.

Esto explica casos reales:

\[
\text{salario alto, mal empleador}
\]

\[
\text{salario bajo, buen propósito}
\]

\[
\text{empresa popular, malas condiciones laborales}
\]

\[
\text{profesión impopular, alto valor social}
\]

---

# 25. Circulación en el mercado de crédito

En el crédito, el dinero se crea de nuevo o se desplaza en el tiempo.

Un banco emite crédito:

\[
\theta_{\text{banco}}^V
\]

El deudor recibe crédito:

\[
\theta_{\text{deudor}}^K
\]

Más tarde el deudor devuelve:

\[
\theta_{\text{deudor}}^V
\]

El banco recibe el reembolso:

\[
\theta_{\text{banco}}^K
\]

Así:

\[
d_{\text{crédito}}=d(\theta_{\text{deudor}}^K,\theta_{\text{banco}}^V)
\]

\[
d_{\text{reembolso}}=d(\theta_{\text{banco}}^K,\theta_{\text{deudor}}^V)
\]

Si el crédito sirve a un buen propósito:

\[
g_{\text{crédito}} \uparrow
\]

Si el crédito financia especulación popular:

\[
b_{\text{crédito}} \uparrow,\quad g_{\text{crédito}} \text{ incierto}
\]

Si el crédito financia actividades tóxicas:

\[
g_{\text{crédito}} \downarrow
\]

Entonces suben los intereses o las garantías.

La tasa de interés se compone de:

\[
i = i_0 + i_{\text{impago}} + i_{\text{riesgo angular}} + i_{\rho}
\]

Es decir:

\[
\text{Interés} = \text{precio del tiempo} + \text{riesgo} + \text{penalización angular}
\]

---

# 26. Circulación en el Estado

El Estado recibe impuestos:

\[
\theta_{\text{Estado}}^K
\]

y realiza gasto público:

\[
\theta_{\text{Estado}}^V
\]

Los impuestos de fuentes tóxicas pueden ser problemáticos:

\[
\text{¿Debe el Estado aceptar dinero malo?}
\]

Si sí, quizá tenga que limpiarlo:

\[
\theta_{\text{tóxico}} \rightarrow \theta_{\text{públicamente legítimo}}
\]

mediante:

- tribunales
- transparencia
- redistribución
- reparación de daños
- inversión pública

El gasto público crea nuevos ángulos:

- La educación puede elevar \(g\).
- La propaganda puede elevar artificialmente \(b\).
- La infraestructura puede elevar valor y bondad.
- La represión puede crear orden a corto plazo, pero mal ángulo a largo plazo.
- La guerra puede recibir ángulos muy distintos según el pueblo y el gobierno.

Por eso el Estado es un enorme transformador angular.

---

# 27. Circulación entre países

Cada país tiene sus propios ejes.

Lo que en el país A es bueno no necesariamente es bueno en el país B.

Por tanto, se necesita traducción angular:

\[
T_{A\rightarrow B}(\theta)
\]

Una operación de exportación tiene entonces:

\[
\theta_{\text{exportación, A}}
\rightarrow
T_{A\rightarrow B}(\theta_{\text{exportación, A}})
\]

Ejemplo:

\[
40^\circ \text{ en el país A}
\]

puede convertirse en:

\[
110^\circ \text{ en el país B}
\]

Entonces surge arbitraje angular internacional.

Las empresas buscan países donde:

- su producto sea más popular
- su bondad se evalúe mejor
- sus malos efectos sean menos visibles
- su historia se revise con menos rigor

Esto es arbitraje moral de localización.

---

# 28. ¿Qué ocurre con varios mercados?

Cada mercado tiene su propia estructura angular.

## Mercado de productos

\[
\theta_{\text{comprador}}^K
\leftrightarrow
\theta_{\text{vendedor}}^V
\]

## Mercado de pagos

\[
\theta_{\text{vendedor}}^K
\leftrightarrow
\theta_{\text{comprador}}^V
\]

## Mercado laboral

\[
\theta_{\text{empresa}}^K
\leftrightarrow
\theta_{\text{trabajador}}^V
\]

y:

\[
\theta_{\text{trabajador}}^K
\leftrightarrow
\theta_{\text{empresa}}^V
\]

## Mercado de crédito

\[
\theta_{\text{deudor}}^K
\leftrightarrow
\theta_{\text{banco}}^V
\]

y más tarde:

\[
\theta_{\text{banco}}^K
\leftrightarrow
\theta_{\text{deudor}}^V
\]

## Mercado de capitales

Los inversores compran participaciones de empresas:

\[
\theta_{\text{inversor}}^K
\leftrightarrow
\theta_{\text{empresa}}^V
\]

Las empresas compran capital:

\[
\theta_{\text{empresa}}^K
\leftrightarrow
\theta_{\text{inversor}}^V
\]

## Mercado angular

Aquí se comercia directamente la dirección:

\[
(m,g,b)
\rightarrow
(m',g',b')
\]

con comisión, riesgo y pérdida de confianza.

---

# 29. Qué significan económicamente los dos ángulos

La diferencia entre ángulo de compra y ángulo de venta es el núcleo de la lógica empresarial:

\[
s_i = d(\theta_i^K,\theta_i^V)
\]

Este es el spread angular del actor.

## Spread pequeño

\[
s_i \approx 0
\]

El actor compra y vende en una dirección similar.

Eso significa:

- coherente
- creíble
- poca transformación
- poco arbitraje
- alta confiabilidad

## Spread grande

\[
s_i \gg 0
\]

El actor compra en una dirección y vende en otra.

Eso puede ser bueno o malo.

### Variante buena

Compra inputs malos y los mejora realmente.

\[
\theta^K = \text{malo}
\]

\[
\theta^V = \text{bueno}
\]

Entonces crea mejora real de valor.

### Variante mala

Compra inputs malos y solo los vende mejor empaquetados.

\[
\theta^K = \text{malo}
\]

\[
\theta^V = \text{aparentemente bueno}
\]

Entonces practica lavado angular.

### Variante extractiva

Compra inputs buenos y vende outputs malos.

\[
\theta^K = \text{bueno}
\]

\[
\theta^V = \text{malo}
\]

Entonces destruye bondad o confianza.

---

# 30. Circulación como ciclo en toda la economía

La economía completa se ve así:

```text
Hogares
  │ compran productos
  ▼
Empresas
  │ pagan salarios, compran inputs, toman créditos
  ▼
Bancos / mercados de capitales
  │ financian empresas y Estados
  ▼
Estados
  │ cobran impuestos, regulan, subvencionan
  ▼
Medios / pueblos / tribunales / gobiernos
  │ evalúan bondad, popularidad y confianza
  ▼
Mercados angulares
  │ rotan, aseguran, auditan y comercian direcciones
  ▼
Hogares y empresas
```

El valor fluye mediante pagos.

La bondad fluye mediante consecuencias reales y juicios institucionales.

La popularidad fluye mediante demanda, medios y aceptación social.

La confianza fluye mediante prueba, transparencia y disputa.

La historia fluye por la cadena de transacciones.

---

# 31. La circulación del dinero se vuelve selectiva

En el dinero normal vale:

\[
100 = 100
\]

En tu sistema vale:

\[
100 \angle 30^\circ \neq 100 \angle 150^\circ
\]

Por eso el dinero ya no circula igual en todas partes.

Se forman zonas:

## Circuito limpio de alta confianza

El buen dinero circula entre actores confiables.

\[
g \uparrow,\quad b \uparrow,\quad \rho \uparrow
\]

Allí los intereses son bajos, el comercio es rápido y los spreads pequeños.

## Circuito popular pero cuestionable

El dinero popular circula rápido, pero con riesgo.

\[
b \uparrow,\quad g \text{ incierto}
\]

Allí hay burbujas y escándalos.

## Circuito bueno pero impopular

Las actividades buenas pero impopulares necesitan paciencia, subvenciones o educación.

\[
g \uparrow,\quad b \downarrow
\]

Allí amenaza la infrafinanciación.

## Circuito tóxico

El dinero malo circula en mercados negros o con grandes descuentos.

\[
g \downarrow,\quad b \downarrow,\quad \rho \downarrow
\]

Allí los intereses son altos, el fraude frecuente y la liquidez baja.

---

# 32. Por qué la circulación no se vuelve automáticamente moral

Un error frecuente sería:

> Si la bondad y la popularidad están dentro del dinero, la economía se vuelve automáticamente buena.

No.

El sistema hace comerciable la dirección moral.

Con ello también la vuelve manipulable.

Conduce a tres formas posibles:

## Mejora real

\[
\text{Valor} \rightarrow \text{bondad real}
\]

## Mejora simbólica

\[
\text{Valor} \rightarrow \text{popularidad}
\]

## Mejora fraudulenta

\[
\text{Valor} \rightarrow \text{bondad aparente}
\]

Por eso \(\rho\), es decir la confianza, es absolutamente central.

Sin confianza, el ángulo se convierte en una etiqueta propagandística.

Con confianza, el ángulo se vuelve verificable.

---

# 33. El mecanismo más breve

La descripción completa más breve es:

\[
\boxed{
\text{Los actores reciben por su ángulo de compra y emiten por su ángulo de venta.}
}
\]

Todo intercambio comprueba:

\[
\boxed{
\text{¿Encaja el ángulo de venta de la mercancía con el ángulo de compra del comprador?}
}
\]

y:

\[
\boxed{
\text{¿Encaja el ángulo de venta del dinero con el ángulo de compra del vendedor?}
}
\]

Si sí, fluyen fácilmente valor, bondad y popularidad.

Si no, aparecen:

- descuentos
- recargos
- rotación
- costes de auditoría
- seguros
- tiempos de espera
- mercados negros
- riesgos reputacionales
- conflictos políticos

La circulación del dinero ya no es un círculo, sino una red dirigida:

\[
\boxed{
\text{El valor fluye a lo largo de ángulos compatibles.}
}
\]

\[
\boxed{
\text{La bondad fluye a lo largo de mejora real y reconocimiento.}
}
\]

\[
\boxed{
\text{La popularidad fluye a lo largo de atención y aprobación.}
}
\]

Los dos ángulos de cada actor determinan **qué quiere absorber** y **qué entrega al mundo**.

De ahí surge exactamente la dinámica económica.
