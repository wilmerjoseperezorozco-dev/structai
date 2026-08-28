import Link from "next/link";
import { ArrowLeft, HardHat } from "lucide-react";

export const metadata = {
  title: "Términos de Uso — StructAI",
};

export default function TerminosPage() {
  return (
    <div className="h-full overflow-y-auto bg-concrete-900 px-4 py-10">
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
        <h1 className="text-3xl font-bold text-white mb-2">Términos de Uso</h1>
        <p className="text-concrete-500 text-xs mb-8">Última actualización: 28 de agosto de 2026</p>

        <div className="bg-concrete-800 border border-concrete-700 rounded-2xl p-6 space-y-6 text-sm text-concrete-300 leading-relaxed">

          <section>
            <h2 className="text-white font-semibold mb-2">1. Quién presta el servicio</h2>
            <p>
              StructAI (nombre de proyecto: Construdata) es operado por Wilmer José Pérez Orozco,
              persona natural, con domicilio en Barranquilla, Atlántico, Colombia. Contacto:{" "}
              <a href="mailto:ventas@structai.online" className="text-brand-400 hover:underline">
                ventas@structai.online
              </a>.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">2. Qué es StructAI</h2>
            <p>
              StructAI es un asistente de apoyo técnico basado en inteligencia artificial para
              ingeniería civil: consulta normativa (NSR-10, NTC), cálculo de Análisis de Precios
              Unitarios (APU), y módulos de cálculo estructural, hidrosanitario, geotécnico, vial
              y de gerencia de proyectos. El servicio se presta bajo un modelo freemium (plan
              gratuito con límites de uso, plan Pro de pago).
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">3. Naturaleza del servicio — límite de responsabilidad profesional</h2>
            <p className="mb-2">
              <strong className="text-white">StructAI es una herramienta de apoyo, no un
              reemplazo del criterio profesional de un ingeniero.</strong> Todos los cálculos,
              interpretaciones normativas y respuestas generadas por el sistema —incluyendo las
              basadas en modelos de lenguaje (IA)— pueden contener errores, omisiones o
              interpretaciones incompletas de la norma vigente.
            </p>
            <p>
              El usuario, y en particular todo profesional que use resultados de la plataforma en
              un diseño, memoria de cálculo o documento firmado, es el único responsable de
              verificar, validar y asumir la responsabilidad técnica y legal de cualquier
              resultado antes de aplicarlo en obra, radicarlo ante una autoridad, o incorporarlo a
              un documento firmado. StructAI no sustituye la firma, el sello ni la
              responsabilidad profesional de un ingeniero matriculado conforme a la ley
              colombiana.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">4. Cuenta de usuario</h2>
            <p>
              Para usar el servicio se requiere una cuenta, autenticada mediante correo y
              contraseña a través de Supabase Auth. El usuario es responsable de mantener la
              confidencialidad de sus credenciales y de toda actividad realizada desde su cuenta.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">5. Planes y pagos</h2>
            <p>
              El plan gratuito tiene límites de uso mensual (APU, proyectos, historial) descritos
              en la página de{" "}
              <Link href="/pricing" className="text-brand-400 hover:underline">planes</Link>.
              El plan Pro es de pago recurrente. El procesamiento de pagos, cuando esté disponible,
              se realizará a través de un proveedor de pagos certificado en Colombia. El usuario
              puede cancelar su suscripción en cualquier momento; la cancelación aplica al ciclo de
              facturación siguiente, sin reembolso del período ya iniciado salvo que la ley
              disponga lo contrario.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">6. Derecho de retracto</h2>
            <p className="mb-2">
              Conforme al artículo 47 de la Ley 1480 de 2011 (Estatuto del Consumidor) y las
              normas de comercio electrónico aplicables en Colombia, si contrataste el plan Pro a
              través de un medio de pago electrónico tienes derecho a retractarte de la compra
              dentro de los cinco (5) días hábiles siguientes a la contratación, sin necesidad de
              justificación. Para ejercer este derecho, escribe a{" "}
              <a href="mailto:ventas@structai.online" className="text-brand-400 hover:underline">
                ventas@structai.online
              </a>{" "}
              indicando tu solicitud; el reembolso se procesará conforme a la ley y a las
              políticas del proveedor de pagos utilizado.
            </p>
            <p>
              Este derecho no aplica si, antes de vencer el plazo anterior, solicitaste
              expresamente y empezaste a usar el servicio contratado — excepción prevista en la
              misma ley para servicios cuya prestación ya inició con el consentimiento expreso del
              consumidor.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">7. Uso aceptable</h2>
            <p>
              No está permitido: usar el servicio para actividades ilegales, intentar vulnerar la
              seguridad de la plataforma, realizar ingeniería inversa del software, revender o
              redistribuir el acceso al servicio sin autorización, o usar el servicio de forma que
              exceda razonablemente los límites técnicos previstos para el plan contratado (por
              ejemplo, automatizar peticiones masivas).
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">8. Propiedad intelectual</h2>
            <p>
              El software, la marca &quot;StructAI&quot; (y el nombre de proyecto &quot;Construdata&quot;), y los contenidos propios de la
              plataforma son propiedad de su operador. Los proyectos, cálculos y datos que el
              usuario introduce en la plataforma siguen siendo de su propiedad; el operador no
              reclama derechos sobre ellos más allá de lo necesario para prestar el servicio.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">9. Disponibilidad y cambios al servicio</h2>
            <p>
              El servicio se presta &quot;tal cual&quot; y &quot;según disponibilidad&quot;. Puede haber
              interrupciones por mantenimiento, fallas de proveedores externos (hosting, IA) o
              causas de fuerza mayor. El operador puede modificar, ampliar o descontinuar
              funciones del servicio, notificando cambios relevantes con antelación razonable
              cuando sea posible.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">10. Ley aplicable</h2>
            <p>
              Estos términos se rigen por las leyes de la República de Colombia. Cualquier
              controversia derivada de su interpretación o aplicación se someterá a la
              jurisdicción de los jueces colombianos.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold mb-2">11. Contacto</h2>
            <p>
              Preguntas sobre estos términos:{" "}
              <a href="mailto:ventas@structai.online" className="text-brand-400 hover:underline">
                ventas@structai.online
              </a>
            </p>
          </section>

        </div>

        <p className="text-center text-xs text-concrete-600 mt-6">
          Ver también la{" "}
          <Link href="/privacidad" className="text-brand-400 hover:underline">
            Política de Privacidad
          </Link>
        </p>
      </div>
    </div>
  );
}
