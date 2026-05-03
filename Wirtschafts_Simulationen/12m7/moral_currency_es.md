# Moneda moral radial-jerárquica

## Pregunta

Un eje es bueno vs. malo y el otro eje es popular vs. impopular. Entonces se puede convertir eso en un número: suma de “niveles jerárquicos: suma de todos los elementos de un nivel jerárquico multiplicada por ese nivel jerárquico”, y también se pueden extraer direcciones angulares de forma arbitraria. Entonces se puede usar esa estructura como moneda y asignar este constructo a todos los objetos de mercado: mercado laboral, mercado de productos, mercado de acciones, mercado de divisas, mercado de seguros. La moneda entonces no es un número, y la moneda da información sobre a quién le corresponde algo: a quien rinde mucho; y la bondad o abnegación de los productos se vuelve reconocible porque los gobiernos del mundo lo fijan, mientras las poblaciones fijan popular vs. impopular. La jerarquía es cambiante: descender, ascender en la carrera, subir, para todo lo que se comercia en los mercados, por ejemplo empleadores y empleados.

## Respuesta

Sí. Lo que describes es, en esencia, una **moneda de valor multidimensional** o un **sistema normativo de coordenadas de mercado**:

\[
\text{valor de mercado} \neq \text{precio}
\]

sino más bien:

\[
\text{valor de mercado} = f(\text{jerarquía}, \text{bondad}, \text{popularidad}, \text{contexto de mercado})
\]

El dinero ya no es solo un número neutral, sino un **estado codificado de derecho o pretensión**: quién recibe algo, vende algo, pierde algo, gana algo o asciende no depende solo del precio, sino de una posición evaluada dentro del sistema.

## 1. Los dos ejes generan cuatro tipos básicos

Si un eje es **bueno ↔ malo** y el otro **popular ↔ impopular**, obtienes cuatro cuadrantes:

| Cuadrante | Significado | Interpretación ejemplar |
|---|---|---|
| **bueno + popular** | socialmente deseado y aceptado | productos útiles, justos y deseados; trabajo respetado |
| **bueno + impopular** | valioso pero subestimado | cuidados, investigación básica, infraestructura necesaria pero impopular |
| **malo + popular** | peligrosamente atractivo | productos adictivos, manipulación, burbujas especulativas, plataformas tóxicas |
| **malo + impopular** | socialmente no deseado | explotación, fraude, productos dañinos |

Esto es potente porque separa algo que los mercados normales suelen mezclar:  
**La popularidad no es lo mismo que la bondad.**

Un producto puede ser popular y dañino. Una actividad puede ser impopular y extremadamente valiosa. Esa distinción es central en tu modelo.

## 2. La jerarquía sería la tercera dimensión

Los ejes “bueno/malo” y “popular/impopular” dan la **dirección**. La jerarquía da la **profundidad, altura o posición de rango**.

Formalmente, un objeto podría describirse así:

\[
V(x) = (G(x), B(x), H(x))
\]

donde:

- \(G(x)\) = bondad, aproximadamente de −1 a +1  
- \(B(x)\) = popularidad, aproximadamente de −1 a +1  
- \(H(x)\) = valor jerárquico, rango, nivel, influencia, profundidad de contribución o posición estructural

Entonces también se puede determinar una dirección angular:

\[
\theta(x) = \operatorname{atan2}(B(x), G(x))
\]

y una magnitud:

\[
r(x) = \sqrt{G(x)^2 + B(x)^2}
\]

Así, un objeto de mercado ya no es simplemente “vale 100 euros”, sino por ejemplo:

\[
x = (\text{muy bueno}, \text{medianamente popular}, \text{nivel jerárquico 7})
\]

Eso sería realmente más una **moneda vectorial** que una moneda numérica.

## 3. Tu fórmula jerárquica es posible, pero necesita normalización

Te refieres aproximadamente a esto:

\[
H = \sum_{k=1}^{n} k \cdot \sum_{i \in L_k} e_i
\]

Es decir: para cada nivel jerárquico \(k\), sumas todos los elementos \(e_i\) de ese nivel y los multiplicas por el nivel.

Eso produce un valor jerárquico ponderado.

Ejemplo:

- Nivel 1: actividad simple
- Nivel 2: actividad especializada
- Nivel 3: actividad coordinadora
- Nivel 4: actividad estratégica
- Nivel 5: actividad que moldea el sistema

Entonces alguien o algo tendría más valor jerárquico si no solo toca muchos elementos, sino que influye en elementos de niveles superiores.

Pero aquí hay un problema: las grandes organizaciones obtendrían automáticamente valores enormes solo porque tienen muchos elementos. Por eso probablemente necesitas una forma normalizada:

\[
H_{\text{norm}} = \frac{\sum_{k=1}^{n} k \cdot \sum_{i \in L_k} e_i}{\sum_{k=1}^{n} \sum_{i \in L_k} e_i}
\]

Entonces no mides solo masa, sino calidad jerárquica media.

De lo contrario siempre gana la corporación más grande, la autoridad más grande o la plataforma más grande.

## 4. Como moneda, esto no sería dinero en el sentido actual

El dinero normal tiene tres funciones principales:

1. **Medio de intercambio**
2. **Unidad de cuenta**
3. **Depósito de valor**

Tu sistema sería más bien:

1. **Medio de intercambio**
2. **Unidad de cuenta**
3. **Depósito de valor**
4. **Indicador moral**
5. **Indicador de estatus**
6. **Indicador de derecho**
7. **Instrumento de control**

Eso es una ampliación enorme.

La moneda entonces no solo dice:

> ¿Cuánto cuesta esto?

Sino también:

> ¿Es bueno?  
> ¿Es popular?  
> ¿Quién gana con ello?  
> ¿A quién le corresponde?  
> ¿Qué posición ocupa en la jerarquía social?  
> ¿Debe promoverse, castigarse, gravarse, preferirse o excluirse?

Conceptualmente es poderoso, pero políticamente extremadamente peligroso.

## 5. El punto más fuerte: los valores de mercado se volverían moralmente visibles

Hoy un precio de mercado puede ocultar mucho.

Un producto barato puede ser barato porque los trabajadores reciben malos salarios.  
Un producto caro puede ser caro aunque sea socialmente inútil.  
Una empresa popular puede ser dañina.  
Un trabajo impopular puede ser indispensable.

Tu modelo diría:

> Un objeto de mercado recibe no solo un precio, sino una firma moral-social visible.

Por ejemplo:

\[
\text{Producto A} = (\text{bueno: }0.8,\ \text{popular: }0.6,\ \text{jerarquía: }4)
\]

\[
\text{Producto B} = (\text{bueno: }-0.7,\ \text{popular: }0.9,\ \text{jerarquía: }6)
\]

El Producto B sería popular e influyente, pero moralmente negativo. En tu sistema podría ser gravado más fuertemente, limitado o devaluado.

Eso es una mejora clara frente a un mercado que solo ve demanda y poder adquisitivo.

## 6. El punto más peligroso: ¿quién define “bueno”?

Dices: los gobiernos del mundo fijan bueno/malo, y las poblaciones fijan popular/impopular.

La división es lógicamente limpia, pero políticamente delicada.

Porque si los gobiernos definen “bueno” y “malo”, surge inmediatamente la pregunta:

> ¿“Bueno” es realmente bueno, o solo conforme al gobierno?

Un Estado podría marcar la disidencia como “mala”.  
Un gobierno podría calificar artificialmente sus propias industrias como “buenas”.  
La oposición, las minorías o la investigación incómoda podrían ser devaluadas.

Entonces la moneda ya no sería solo un instrumento de mercado, sino un **instrumento de dominación**.

La población como fuente de popularidad tiene otro problema:

> La popularidad es manipulable.

Quien posee poder mediático, poder de plataforma, publicidad, bots, influencia cultural o celebridad puede fabricar popularidad artificialmente. Entonces no se vuelve popular lo bueno, sino lo mejor manipulado.

Por eso tu modelo necesitaría mecanismos de protección:

- justificaciones transparentes para las evaluaciones bueno/malo
- derechos de apelación
- órganos de revisión independientes
- protección de minorías
- reglas contra la manipulación de la popularidad
- separación entre evaluación moral y lealtad política
- retrasos temporales contra el bombo y el pánico
- valores de incertidumbre en lugar de juicios absolutos

De lo contrario se convierte muy rápido en un sistema de crédito social perfeccionado.

## 7. “A quién le corresponde algo” es el núcleo verdaderamente radical

La frase más importante de tu idea no es la geometría, sino esta:

> La moneda da información sobre a quién le corresponde algo.

Con eso abandonas el mercado normal.

Un mercado clásico dice:

> Quien puede pagar, lo recibe.

Tu sistema dice más bien:

> Quien lo merece, actúa con bondad, es socialmente útil y está adecuadamente situado en la jerarquía recibe una pretensión más fuerte.

Es una mezcla de:

- meritocracia
- economía moral
- sistema de reputación
- asignación política
- mecanismo de mercado
- orden de estatus

Esto puede ser más justo que el capitalismo puro, pero solo si la lógica de evaluación es muy robusta. De lo contrario surge un nuevo orden de clases: las personas y organizaciones con puntuación alta obtienen todo; las de puntuación baja quedan excluidas.

Una versión sana probablemente tendría que decir:

> Los derechos fundamentales y la provisión básica nunca deben depender por completo de esta moneda.

De lo contrario, el orden moral de mercado se convierte en un sistema de castas.

## 8. En los mercados laborales sería especialmente interesante

Empleadores y empleados podrían ser evaluados ambos.

Un empleado podría tener, por ejemplo:

\[
A = (\text{rendimiento}, \text{bondad}, \text{popularidad}, \text{nivel jerárquico})
\]

Un empleador igualmente:

\[
U = (\text{productividad}, \text{justicia}, \text{beneficio social}, \text{popularidad}, \text{nivel de poder})
\]

Entonces la pregunta ya no sería solo:

> ¿Cuánto paga el empleador?

Sino también:

> ¿Es bueno este empleador?  
> ¿Sus productos son buenos?  
> ¿Trata justamente a las personas?  
> ¿Su popularidad es merecida o manipulada?  
> ¿Su posición moral de mercado sube o baja?

Eso haría los mercados laborales más simétricos. Hoy el empleador suele evaluar al empleado más que al revés. En tu modelo, ambas partes se volverían visibles jerárquica y moralmente.

## 9. En los mercados bursátiles, teñiría moralmente la especulación

Una acción ya no sería solo:

\[
\text{precio} + \text{expectativa de rendimiento}
\]

sino:

\[
\text{precio} + \text{rendimiento} + \text{bondad} + \text{popularidad} + \text{rango sistémico}
\]

Una empresa rentable pero dañina podría tener un alto valor económico, pero un vector moral negativo.

Los inversores ya no podrían decir invisiblemente:

> Me da igual, mientras haya rendimiento.

La moneda mostraría:

> Este rendimiento proviene de un ámbito evaluado negativamente.

Eso podría cambiar fuertemente los flujos de capital.

## 10. En los mercados de productos, la “abnegación” es difícil, pero no imposible

Los productos en sí no son abnegados. Las personas, organizaciones o diseños pueden ser abnegados o explotadores. En productos habría que medir más bien:

- utilidad para los compradores
- daño a terceros
- costes ambientales
- condiciones laborales
- potencial de dependencia/adicción
- reparabilidad
- transparencia
- distribución de beneficios
- efecto social a largo plazo

Entonces la “bondad del producto” no sería psicológica, sino un **perfil de externalidades**.

Un medicamento que salva vidas sería bueno.  
Un producto adictivo con marketing agresivo podría ser popular, pero negativamente bueno.  
Un producto de infraestructura aburrido pero importante sería bueno, aunque quizá impopular.

Precisamente para eso sirve tu sistema de ejes.

## 11. El mercado no desaparecería, sino que sería filtrado

Tu sistema no sustituye completamente los mercados. Coloca una capa normativa sobre ellos.

Hoy:

\[
\text{transacción permitida si se paga el precio}
\]

En tu sistema:

\[
\text{transacción permitida/rebajada/dificultada según la posición vectorial}
\]

Es decir:

- Las cosas buenas y populares se facilitan.
- Las cosas buenas pero impopulares se protegen o subsidian.
- Las cosas malas pero populares se frenan.
- Las cosas malas e impopulares se excluyen o se cargan fuertemente.

Es una lógica bastante elegante.

## 12. Pero una moneda real necesita compatibilidad

Un problema: si la moneda no es un número, ¿cómo se comparan dos cosas?

Ejemplo:

\[
X = (\text{bueno }0.9,\ \text{popular }0.1,\ H=3)
\]

\[
Y = (\text{bueno }0.2,\ \text{popular }0.9,\ H=7)
\]

¿Cuál vale más?

Eso no puede decidirse objetivamente mientras no tengas una regla de comparación. Necesitas una de estas opciones:

### Variante A: Escalarización

Conviertes todo en un número:

\[
S = \alpha G + \beta B + \gamma H
\]

Ventaja: fácil de comerciar.  
Desventaja: pierdes la multidimensionalidad.

### Variante B: Moneda vectorial

Mantienes todas las dimensiones:

\[
V = (G, B, H)
\]

Ventaja: información más rica.  
Desventaja: intercambio más difícil, porque no todo es claramente comparable.

### Variante C: Regla de comparación dependiente del contexto

Según el mercado se aplican pesos distintos.

En el mercado sanitario cuenta más la bondad.  
En el mercado del entretenimiento cuenta más la popularidad.  
En el mercado laboral cuenta más el rendimiento/la jerarquía.  
En el mercado de seguros cuentan más el riesgo y la responsabilidad.

Probablemente esta sería la mejor variante.

## 13. La forma más elegante no sería una moneda única, sino un protocolo de valor

Yo formularía tu modelo así:

> No es la moneda misma la que es multidimensional; más bien, cada unidad de mercado porta un vector de valor, y cada transacción se filtra mediante un protocolo social de evaluación.

Entonces:

\[
\text{transacción} = (\text{precio}, \text{vector de valor}, \text{regla de derecho})
\]

Así el dinero sigue siendo utilizable en la práctica, pero ya no es ciego.

Eso es más fuerte que decir: “La moneda no es un número.”  
Más precisamente:

> El precio sigue siendo un número, pero la validez, calidad y legitimidad del precio dependen de un vector de valor multidimensional.

## 14. Mi evaluación

La idea es conceptualmente fuerte porque une tres cosas que normalmente están separadas:

1. **Jerarquía / rendimiento / rango**
2. **Calidad moral**
3. **Aceptación social**

Con ello se pueden representar los mercados de manera mucho más inteligente que solo mediante el precio.

Pero tiene un punto de quiebre duro:

> En cuanto “lo bueno” se define centralmente y las pretensiones económicas dependen de ello, surge un enorme aparato de poder.

Por eso la mejor versión no sería:

> El gobierno determina absolutamente bueno/malo.

Sino:

> Gobierno, población, ciencia, tribunales, comportamiento de mercado y datos de impacto verificables proporcionan señales separadas, a partir de las cuales surge un vector de valor transparente.

Entonces el sistema sería menos tiránico y más orientado al conocimiento.

En una frase:

**Describes una moneda moral radial-jerárquica y vectorial que ordena los mercados no solo por precio, sino por bondad, popularidad y posición de rango — teóricamente muy poderosa, pero en la práctica solo segura si la evaluación, la apelación, la protección de minorías y la defensa contra la manipulación se toman extremadamente en serio.**
