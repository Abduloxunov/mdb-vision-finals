# Deploy CarDoctor now (step by step)

Everything is on branch `claude/technician-map` → **PR #7**: https://github.com/Abduloxunov/mdb-vision-finals/pull/7

## 1. Merge (1 min)
GitHub → PR #7 → **Merge pull request**.

## 2. Make the repo public (1 min)
GitHub → mdb-vision-finals → Settings → General → Danger Zone → **Change visibility → Public**.

## 3. Upload the trained weights to a PRIVATE Hugging Face repo (2 min, laptop, Git Bash)
```bash
cd /d/hakathon_wiut/finals/mdb-vision-finals
git checkout main && git pull origin main
pip install -U huggingface_hub
huggingface-cli login          # paste a WRITE token from huggingface.co/settings/tokens
huggingface-cli upload Abduloxunov/cardoctor-weights \
  experiments/cardoctor-hf/.runtime/downloaded-continuation-12/checkpoint_best_ema.pth \
  checkpoint_best_ema.pth --repo-type model --private
```

## 4. Create the Space (1 min)
https://huggingface.co/new-space → Owner **Abduloxunov**, name **cardoctor**, SDK **Docker** (blank), hardware **CPU basic**, Public → Create.

Space → **Settings → Variables and secrets**:
- **New secret** `HF_TOKEN` = a READ token (it can be the same token)
- **New variable** `CARDOCTOR_WEIGHTS_REPO` = `Abduloxunov/cardoctor-weights`
- (optional) **New secret** `OPENROUTER_API_KEY` = the key from your `.env`

## 5. Push the code to the Space (1 min + 5–10 min build)
```bash
git remote add space https://huggingface.co/spaces/Abduloxunov/cardoctor
git push space main            # username = Abduloxunov, password = the WRITE token
```
If it says the Space already has a commit: `git push space main --force` (the Space only has its template README).

Watch Space → **Logs**. Done when you see: `CarDoctor warm-up finished: ready`.

## 6. Test on your phone
Open **https://abduloxunov-cardoctor.hf.space**
1. **Sample 1: BYD Seal** → Check the car → verdict, damage boxes, **3D car** with red areas
2. **📍 Use my location** → nearest technicians, **🧭 Route**, **🗺 Find real workshops near me**
3. Fleet & trucks → "Chevrolet Cobalt", "engine overheating, steam" → 🔴 Stop and get help

## 7. Submit (team dashboard)
- Prototype: `https://abduloxunov-cardoctor.hf.space`
- Deck: PDF/PPTX
- Repo: `https://github.com/Abduloxunov/mdb-vision-finals`

**If the build fails or isn't ready by 13:00:** submit anyway, and paste the Logs error to Claude. Backup link: on your laptop run `python -B src/app.py`, then in a second window `cloudflared tunnel --url http://127.0.0.1:8766 --http-host-header localhost:8766`.
