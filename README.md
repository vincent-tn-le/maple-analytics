# Maple Analytics
Analytics of late to end game players on Maplestory to capture trends in leveling, meta, and potential botters


Structure:
Lambda (hourly) → S3 raw JSON → Glue/Spark → S3 Parquet → Redshift Serverless
                           ↓                                    ↓
                       dbt models                    FastAPI + Streamlit
                          (Gold)                              (UI + API)

Key Tables:
Name	Grain	Purposes
player_dim	immutable character_id	lookup (world, name, first_seen, job, job_group)
rank_fact	character_id × snapshot	rank, level, exp, guild_id
rank_velocity_fact	derived: Δ vs. previous snapshot	rank_diff, exp_diff, hours_between
class_meta_day	world × job_group × date	total_≥280, share_pct
bot_risk_fact	character × date	risk_score, flagged_reason