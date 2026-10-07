# Protocolo común de ingestión de datasets humanos

**Estado:** diseño  
**Fecha:** 2026-10-07

## Objetivo

Incorporar datasets humanos heterogéneos sin alterar el fenómeno original ni imponer una representación quantum-like.

## Pipeline

dataset → adapter → canonical observations → experiment → model → metrics → report

El adaptador no contiene lógica específica del modelo.

## Esquema canónico

Campos preferentes: participant_id, trial_id, task_id, stimulus_id, condition, context, sequence_index, response, response_time, confidence, source, session, language, group.

Los campos ausentes permanecen como missing; no se inventan valores.

## Reproducibilidad

Registrar fuente primaria, DOI/URL, versión, fecha de acceso, licencia, checksum cuando sea posible, transformaciones, exclusiones, participantes y observaciones finales.

## No leakage

La partición train/test debe respetar la unidad experimental. No dividir ensayos del mismo participante entre train y test cuando produzca fuga de información individual. En datos longitudinales evaluar particiones temporales.

## Modelado

Todo modelo quantum-like debe compararse con al menos un baseline clásico razonable. Un buen ajuste aislado no demuestra superioridad.

Cada experimento declara parámetros, restricciones, métricas y procedimiento de validación antes de interpretar los resultados.

## Métricas

Según el fenómeno: log-likelihood, Brier score, cross-entropy, accuracy, calibration, RMSE/MAE, predictive log score, error de transición, distancia entre distribuciones y QQ residual cuando corresponda. AIC/BIC requieren cautela en modelos singulares o no identificables.

## Resultado epistemológico

Cada experimento debe producir reproducción descriptiva, comparación de modelos, incertidumbre y conclusión clasificada como: evidencia a favor, evidencia contra, evidencia insuficiente, dependiente del baseline o no identificable.

## Transferencia

Solo resultados suficientemente validados pueden alimentar Psyche Simulacra, el cerebro digital o Hanna. Toda transferencia debe conservar fenómeno de origen, dataset, modelo, parámetros, incertidumbre, límites de generalización, versión y evidencia de respaldo.

## Regla

La investigación descubre. El modelado formaliza. La transferencia reutiliza. Ninguna capa puede modificar retrospectivamente el resultado de otra.
