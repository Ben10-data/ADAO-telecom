WITH mart_offer AS (
    SELECT * FROM {{ref("union_table")}}

), 

offers AS (
    SELECT operator, country, offer_name, offer_type_clean as offer_type,
    volume_data_gb, 
    speed_mbps, 
    price_eur as prix_euro,media_type_clean as media_type, 
    validity_days, is_unlimited, 
    ROUND(estimated_monthly_income_eur::NUMERIC, 2) as salaire_estim_euro, cost_per_gb_eur, dai_pct

    FROM mart_offer
    WHERE volume_data_gb IS NOT NULL OR speed_mbps IS NOT NULL
)

select * from offers 

