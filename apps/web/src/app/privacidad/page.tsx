import Link from "next/link";
import { ArrowLeft, HardHat } from "lucide-react";

export const metadata = {
  title: "Política de Privacidad — StructAI",
};

export default function PrivacidadPage() {
  return (
    <div className="min-h-full bg-concrete-900 px-4 py-10">
      <div className="max-w-2xl mx-auto">
        <Link
          href="/login"
          className="inline-flex items-center gap-1.5 text-xs text-concrete-400 hover:text-concrete-200 transition mb-6"
        >
          <ArrowLeft size={14} />
          Volver
        </Link>

        <div className="inline-flex items-center gap-2 mb-4 px-3 py-1.5 bg-brand-900/50 border border-brand-700/40 rounded-full">
          <HardHat size={14} className="text-brand-400" />
          <span className="text-xs text-brand-300 font-medium">StructAI</span>
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">Política de Privacidad</h1>
        <p className="text-concrete-500 text-xs mb-1">Última actualización: 13 de julio de 2026</p>
        <p className="text-concrete-500 text-xs mb-8">
          Aviso de privacidad conforme a la Ley 1581 de 2012 (Habeas Data) y sus decretos reglamentarios.
        </p>

        <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-6 space-y-6 text-sm text-concrete-300 leading-relaxed">

          <section>
            <h2 className="text-white font-semibold mb-2">1. Responsable del tratamiento</h2>
            <p>
              Wilmer José Pérez Orozco, persona natural, domiciliado en Barranquilla, Atlántico,
              Colombia, operador de StructAI (nombre de proyecto: Construdata). Correo de contacto
              para asuntos de datos personales:{" "}
              <a href="mailto:wilmerjoseperezorozco@gmail.com" className="text-brand-400 hover:underline">
                wilmerjoseperezorozco@gmail.com
              </a>.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">2. Qué datos recolectamos</h2>
            <ul className="list-disc list-inside space-y-1">
              <li>Correo electrónico y contraseña, al crear una cuenta (autenticación vía Supabase Auth; la contraseña nunca se almacena en texto plano).</li>
              <li>Contenido de las consultas técnicas y proyectos que el usuario ingresa a la plataforma (preguntas normativas, datos de APU, parámetros de cálculo).</li>
              <li>Datos de uso del servicio: número de APU calculados por mes, cantidad de proyectos, historial de consultas — necesarios para aplicar los límites del plan gratuito/Pro.</li>
              <li>Imágenes que el usuario suba voluntariamente para detección estructural, si usa esa función.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">3. Para qué usamos estos datos</h2>
            <ul className="list-disc list-inside space-y-1">
              <li>Autenticar al usuario y mantener su sesión.</li>
              <li>Prestar el servicio solicitado (cálculos, respuestas normativas, gestión de proyectos).</li>
              <li>Medir y aplicar los límites de uso del plan contratado (freemium/Pro).</li>
              <li>Diagnosticar fallas técnicas y mejorar el servicio.</li>
            </ul>
            <p className="mt-2">No usamos los datos del usuario con fines publicitarios ni los vendemos a terceros.</p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">4. Con quién compartimos datos (encargados del tratamiento)</h2>
            <p className="mb-2">
              Para operar el servicio usamos proveedores externos que procesan datos por
              encargo nuestro:
            </p>
            <ul className="list-disc list-inside space-y-1">
              <li><strong className="text-white">Supabase</strong> — almacenamiento de la base de datos y autenticación de usuarios.</li>
              <li><strong className="text-white">Groq</strong> — procesamiento de las consultas mediante modelos de inteligencia artificial. El texto de la consulta se envía a este proveedor para generar la respuesta.</li>
              <li><strong className="text-white">Vercel</strong> — hospedaje de la aplicación web.</li>
            </ul>
            <p className="mt-2">
              Estos proveedores operan con infraestructura fuera de Colombia, por lo que el uso
              del servicio implica una transferencia internacional de datos necesaria para su
              funcionamiento. No compartimos datos con terceros para fines distintos a la
              prestación del servicio.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">5. Cuánto tiempo conservamos los datos</h2>
            <p>
              Mientras la cuenta del usuario permanezca activa. Si el usuario solicita la
              eliminación de su cuenta, sus datos personales se eliminan en un plazo razonable,
              salvo que exista una obligación legal de conservarlos por más tiempo.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">6. Derechos del titular de los datos (derechos ARCO)</h2>
            <p className="mb-2">Como titular de tus datos personales, tienes derecho a:</p>
            <ul className="list-disc list-inside space-y-1">
              <li><strong className="text-white">Acceso:</strong> conocer qué datos tuyos tenemos.</li>
              <li><strong className="text-white">Rectificación:</strong> corregir datos inexactos o desactualizados.</li>
              <li><strong className="text-white">Cancelación/supresión:</strong> solicitar que eliminemos tus datos cuando ya no sean necesarios o retires tu autorización.</li>
              <li><strong className="text-white">Oposición:</strong> oponerte a un tratamiento específico de tus datos.</li>
              <li>Revocar en cualquier momento la autorización otorgada.</li>
            </ul>
            <p className="mt-2">
              Para ejercer cualquiera de estos derechos, escribe a{" "}
              <a href="mailto:wilmerjoseperezorozco@gmail.com" className="text-brand-400 hover:underline">
                wilmerjoseperezorozco@gmail.com
              </a>. Responderemos tu solicitud dentro de los plazos que establece la ley
              colombiana (10 días hábiles para consultas, 15 días hábiles para reclamos).
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">7. Seguridad de la información</h2>
            <p>
              El acceso a la plataforma se realiza mediante conexión cifrada (HTTPS). Las
              contraseñas se gestionan mediante Supabase Auth, que aplica hash criptográfico y
              nunca almacena contraseñas en texto plano.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">8. Queja ante la autoridad</h2>
            <p>
              Si consideras que el tratamiento de tus datos personales vulnera la ley, puedes
              presentar una queja ante la Superintendencia de Industria y Comercio (SIC),
              autoridad de protección de datos en Colombia.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">9. Cambios a esta política</h2>
            <p>
              Esta política puede actualizarse para reflejar cambios en el servicio o en la
              normativa aplicable. La fecha de &quot;última actualización&quot; en la parte superior
              indica la versión vigente.
            </p>
          </section>

        </div>

        <p className="text-center text-xs text-concrete-600 mt-6">
          Ver también los{" "}
          <Link href="/terminos" className="text-brand-400 hover:underline">
            Términos de Uso
          </Link>
        </p>
      </div>
    </div>
  );
}
