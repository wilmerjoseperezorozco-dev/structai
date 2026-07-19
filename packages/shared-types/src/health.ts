// apps/api's /health handler returns a plain dict without response_model,
// así que no aparece en /openapi.json — este tipo se mantiene a mano y hay
// que revisarlo si cambia la forma real de la respuesta en apps/api/main.py.
export interface HealthResponse {
  status: string;
  version: string;
  modulos: {
    rag_multi_norma: boolean;
    motor_apu: boolean;
    motor_deformacion: boolean;
    motor_aquai: boolean;
    motor_geopot: boolean;
    motor_vias: boolean;
    motor_gerencia: boolean;
    yolo_onnx: boolean;
    yolo_deps: boolean;
  };
  apu_count: number;
}
