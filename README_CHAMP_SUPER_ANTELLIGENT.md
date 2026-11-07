# CHAMP_SUPER_ANTELLIGENT - SINGLE NAME - NO VERSION - FORMAL - ISO 19650 - LOCKED
# Submission folder: 99_SUBMISSION_FOR_META_READY_TO_SUBMIT
# Repair in place only - DO NOT create new project / folder / FINAL / V2 / V3 / BACKUP / ZIP

## CODE READY - 6 Engines + 3 Adapters
- BOQ Engine: Grand = (Area * 741 * SoilMult * SlopeMult * AccessMult) + Pile + Barrier + Drain + Plant + System + OH15% + Profit10% + VAT7%. BaseRate 741 = 320207 / 432 from 88/1. 88/1 base 320112 vs invoice 320207 diff 0.03%. With add-ons double-count 112% - see boq_engine.py. PJ0014 NOT VERIFIED - keep truthful 510277 vs 311753.
- Soil Engine: USDA 12 Orders. Vertisols = Clay >30% to 50cm AND COLE >=0.09 + slickensides + smectite. DATA_GATE #4231 blocks Vertisols without SPT. Fixes: Pile D30 L2-3m, Barrier HDPE 80cm, Slot Drain 1-2%.
- Plant Engine: 20 REAL species with scientific names, linked to soil tolerance.
- ASTM Engine: SPT D1586 Hammer 63.5kg Drop 760mm Seating 150mm N = last 300mm. EI D4829 EI = 1000*(hf-hi)/hi. 0-20 Very Low, 21-50 Low, 51-90 Medium, 91-130 High, >130 Very High.
- LEED Engine: LEED v5 110 points, 8 categories IP LT SS WE EA MR EQ PP, Certified 40-49 Silver 50-59 Gold 60-79 Platinum 80+, April 2025.
- SOP Engine: 45 Days 13 Phases - planning target, not guarantee. Days 1-3 Survey+SPT to Days 44-45 Handover + Warranty 1 year.
- Adapters: Meta muse-spark-1.3 via https://api.meta.ai/v1/chat/completions MODEL_API_KEY, Gemini gemini-3.8-flash via google-genai GEMINI_API_KEY, Modal Muse Spark Open via MODAL_PROXY_TOKEN /v1/models /v1/chat/completions MODAL_MUSE_SPARK_OPEN. All EXPLANATION_ONLY per Rule 6. Env only - NEVER hardcode.

## [DOCUMENTATION_ONLY] - NOT CODE READY - Do NOT promote
- 135 Agents = [DOCUMENTATION_ONLY] - Actual 6 engines + 3 adapters
- 500 Plant species = [DOCUMENTATION_ONLY] - Actual 20 real
- 100 Projects = [DOCUMENTATION_ONLY] - Actual 2 real references PJ0014 + 88/1
- 384-dim Vector DB = [DOCUMENTATION_ONLY]
- 15 Subsystems On/Off, HMAC gate, Rate Limit 100/15min, Fernet, Kill Switch = [DOCUMENTATION_ONLY] - Actual: simple audit log, Rate limiting NOT_IMPLEMENTED, API auth NOT_IMPLEMENTED

## DEPLOYMENT - Vercel (Frontend) + Cloud Run (Backend)
- Backend: gcloud run deploy champ-super-antelligent --source . --set-env-vars MODEL_API_KEY=$MODEL_API_KEY,GEMINI_API_KEY=$GEMINI_API_KEY,MODAL_PROXY_TOKEN=$MODAL_PROXY_TOKEN - Dockerfile provided. Never bake keys into image.
- Frontend: Vercel import same repo, set NEXT_PUBLIC_API_URL=https://<cloud-run-url>, vercel.json rewrites /api/* to Cloud Run. Replace CHAMP-SUPER-ANTELLIGENT-BACKEND-URL with real Cloud Run URL.
- Test: GET /api/health must show provider_registry [meta,gemini,modal]. POST /api/boq/calculate Area 100 Soil Vertisols SPT 8 -> Grand truthful.
- Security: No wk- ws- Bearer tokens, API keys, passwords in docs. Env only. sanitize_input regex ^[a-zA-Z0-9 _-.()%]+$ length 100. DATA_GATE #4231.

## FILES - FINAL CLEAN STRUCTURE - CHAMP_SUPER_ANTELLIGENT
app.py, boq_engine.py, soil_engine.py, plant_engine.py, astm_engine.py, leed_engine.py, sop_engine.py, adapters/meta_adapter.py, adapters/gemini_adapter.py, adapters/modal_adapter.py, Dockerfile, vercel.json, requirements.txt, README_CHAMP_SUPER_ANTELLIGENT.md

Evidence > Claims. Repair > Rebuild. One CHAMP > Many Versions.
