{{ config(materialized='table') }}

WITH offres_normalisees AS (
    SELECT 
        country AS pays,
        operator,
        offer_name,
        offer_type_clean AS offer_type,
        volume_data_gb, source_url,
        validity_days,
        price_eur,
        estimated_monthly_income_eur,
        
        CASE
            WHEN validity_days > 0 AND validity_days <> 30
            THEN ROUND((price_eur / validity_days)::numeric * 30, 2)
            ELSE price_eur
        END AS price_month_eur,
        
        -- Normalisation du volume sur 30 jours
        CASE
            WHEN validity_days > 0 AND validity_days <> 30
            THEN ROUND((volume_data_gb / validity_days)::numeric * 30, 2)
            ELSE volume_data_gb
        END AS volume_month_gb,
        
        -- Coût par Go (normalisé)
        CASE
            WHEN validity_days > 0 AND validity_days <> 30
            THEN ROUND((((price_eur / validity_days) * 30) / ((volume_data_gb / validity_days) * 30))::numeric, 3)
            ELSE ROUND((price_eur / volume_data_gb)::numeric, 3)
        END AS cout_go_eur,
        
        -- DAI (basé sur le prix normalisé)
        CASE
            WHEN validity_days > 0 AND validity_days <> 30
            THEN ROUND((((price_eur / validity_days) * 30) / estimated_monthly_income_eur * 100)::numeric, 2)
            ELSE ROUND((price_eur / estimated_monthly_income_eur * 100)::numeric, 2)
        END AS dai_pct
        
    FROM {{ ref("union_table") }}
    WHERE volume_data_gb >= 10
      AND price_eur > 0
),

classement AS (
    SELECT 
        pays,
        operator,
        offer_type,offer_name, source_url, 
        volume_data_gb AS volume_original_go,
        validity_days AS validite_jours,
        ROUND(price_eur::numeric, 2) AS prix_original_eur,
        volume_month_gb AS volume_mensuel_go,
        ROUND(price_month_eur::numeric, 2) AS prix_mensuel_eur,
        cout_go_eur,
        dai_pct,
        
        -- Rang par pays (offre la moins chère en premier)
        ROW_NUMBER() OVER (PARTITION BY pays ORDER BY price_month_eur ASC) AS rang_dans_pays
        
    FROM offres_normalisees
)

SELECT *
FROM classement
ORDER BY prix_mensuel_eur ASC