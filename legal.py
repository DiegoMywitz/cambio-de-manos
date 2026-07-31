FECHA_VIGENCIA = "30 de julio de 2026"

TERMINOS = f"""
### Términos y Condiciones de Uso

*Última actualización: {FECHA_VIGENCIA}*

**1. Qué es Cambio de Manos**

Cambio de Manos es una plataforma que conecta personas que quieren vender un
fondo de comercio o una empresa con personas interesadas en comprarlo.
Actuamos únicamente como **intermediarios de contacto**: publicamos los
avisos que cargan los vendedores y facilitamos que los interesados dejen una
consulta. No somos parte de ninguna negociación, no verificamos la veracidad
de los datos financieros cargados por los vendedores, no garantizamos el
resultado de ninguna operación y no cobramos comisión sobre el valor de las
transacciones que se cierren entre las partes.

**2. Cuenta de usuario**

Para publicar un negocio o dejar una consulta es necesario crear una cuenta
con un email real y una contraseña. Sos responsable de mantener la
confidencialidad de tu contraseña y de toda actividad que ocurra desde tu
cuenta.

**3. Contenido publicado**

Al publicar un negocio, declarás que los datos cargados (precio, facturación,
ganancia, antigüedad, fotos, descripción, etc.) son reales y que tenés
derecho a ofrecer ese negocio en venta. Cambio de Manos puede remover
cualquier publicación que considere falsa, engañosa, o que infrinja estos
términos, sin necesidad de aviso previo.

**4. Pagos**

Algunas modalidades de publicación (por ejemplo, el nivel "Destacado") tienen
un costo, que se cobra a través de Mercado Pago. El pago corresponde
únicamente a la visibilidad de la publicación en la plataforma, no a ningún
resultado de venta.

**5. Límite de responsabilidad**

Cambio de Manos no participa en la due diligence, la valuación, ni la
negociación entre comprador y vendedor. Cualquier acuerdo, contrato o pago
que se realice como consecuencia de un contacto originado en la plataforma es
exclusiva responsabilidad de las partes involucradas. Recomendamos siempre
asesorarse con un contador y un abogado antes de comprar o vender un fondo de
comercio o una empresa.

**6. Modificaciones**

Podemos actualizar estos términos en cualquier momento. Los cambios rigen
desde su publicación en esta misma página.

**7. Contacto**

Consultas sobre estos términos: cambiodefirma.contacto@gmail.com
"""

PRIVACIDAD = f"""
### Política de Privacidad

*Última actualización: {FECHA_VIGENCIA}*

En cumplimiento de la Ley 25.326 de Protección de Datos Personales de la
República Argentina, te informamos cómo tratamos tus datos en Cambio de
Manos.

**1. Qué datos recolectamos**

- Datos de cuenta: nombre, email, teléfono (opcional), contraseña (guardada
  siempre con hash, nunca en texto plano).
- Datos de las publicaciones: los que cargue el vendedor sobre su negocio
  (rubro, ubicación, precio, facturación, fotos, etc.).
- Datos de consultas: el mensaje que un interesado le escribe a un vendedor.

**2. Para qué los usamos**

- Mostrar tu publicación a otros usuarios de la plataforma.
- Avisarte por email cuando alguien deja una consulta sobre tu publicación,
  cuando pedís recuperar tu contraseña, o cuando aparece un negocio nuevo que
  coincide con una alerta de búsqueda que guardaste.
- Verificar tu identidad como titular de la cuenta.

**3. Con quién compartimos tus datos**

Cuando dejás una consulta sobre un negocio, tu nombre, email y teléfono se
comparten con el vendedor de esa publicación (y viceversa: si sos vendedor,
tus datos de contacto quedan visibles para quien consulta), para que puedan
comunicarse directamente. No vendemos ni cedemos tus datos a terceros con
fines publicitarios.

**4. Dónde se guardan**

Los datos se almacenan en una base de datos (Supabase/Postgres) con acceso
restringido. Las contraseñas se guardan con hash (PBKDF2), nunca en texto
plano.

**5. Tus derechos**

Como titular de tus datos personales, tenés derecho a acceder, rectificar,
actualizar o solicitar la supresión de tus datos en cualquier momento,
escribiendo a cambiodefirma.contacto@gmail.com. También podés ejercer tus
derechos ante la Agencia de Acceso a la Información Pública
(www.argentina.gob.ar/aaip), órgano de control de la Ley 25.326.

**6. Contacto**

Consultas sobre esta política: cambiodefirma.contacto@gmail.com
"""
