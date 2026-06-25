{{ config(materialized='table') }}

WITH offres_illimitees AS (
    SELECT 
        country AS pays,
        operator,
        offer_name,
        offer_type_clean AS offer_type,
        speed_mbps,
        source_url,
        validity_days,
        price_eur,
        estimated_monthly_income_eur,
        
        -- Normalisation du prix sur 30 jours
        CASE
            WHEN validity_days > 0 AND validity_days <> 30
            THEN ROUND((price_eur / validity_days)::numeric * 30, 2)
            ELSE price_eur
        END AS price_month_eur,
        
        -- Coût par Mbps (normalisé)
        CASE
            WHEN speed_mbps > 0
            THEN ROUND((price_eur / speed_mbps)::numeric, 2)
            ELSE NULL
        END AS cout_mbps_eur,
        
        -- DAI (basé sur le prix normalisé)
        CASE
            WHEN validity_days > 0 AND validity_days <> 30
            THEN ROUND((((price_eur / validity_days) * 30) / estimated_monthly_income_eur * 100)::numeric, 2)
            ELSE ROUND((price_eur / estimated_monthly_income_eur * 100)::numeric, 2)
        END AS dai_pct
        
    FROM {{ ref("union_table") }}
    WHERE speed_mbps IS NOT NULL
      AND speed_mbps > 0
      AND price_eur > 0
      AND offer_type_clean <> 'ligne_speciale'
      AND offer_type_clean <> 'mobile'
      -- Exclure les offres trop courtes (moins de 7 jours)
      AND (validity_days IS NULL OR validity_days >= 7)
),

classement AS (
    SELECT 
        pays,
        operator,
        offer_type,
        offer_name,
        source_url,
        speed_mbps AS debit_mbps,
        validity_days AS validite_jours,
        ROUND(price_eur::numeric, 2) AS prix_original_eur,
        ROUND(price_month_eur::numeric, 2) AS prix_mensuel_eur,
        cout_mbps_eur,
        dai_pct,
        
        -- Rang par pays (offre la moins chère au Mbps en premier)
        ROW_NUMBER() OVER (PARTITION BY pays, offer_type ORDER BY cout_mbps_eur ASC) AS rang_dans_pays
        
    FROM offres_illimitees
)

SELECT *
FROM classement
ORDER BY cout_mbps_eur ASC