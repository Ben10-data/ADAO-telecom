WITH mart_operator AS (
    SELECT *
    FROM {{ ref("union_table") }}
),

resume_pays AS (
    SELECT
        operator,
        offer_name,
        offer_type_clean AS offer_type,
        country AS pays,
        estimated_monthly_income_eur,
        
        CASE
            WHEN validity_days IS NOT NULL
                 AND validity_days > 0
                 AND validity_days <> 30
            THEN ROUND((price_eur / validity_days)::numeric * 30, 2)
            ELSE price_eur
        END AS price_month_eur,
        
        CASE
            WHEN validity_days IS NOT NULL
                 AND validity_days > 0
                 AND validity_days <> 30
            THEN ROUND((volume_data_gb / validity_days)::numeric * 30, 2)
            ELSE volume_data_gb
        END AS volume_month_data

    FROM mart_operator
    WHERE is_unlimited IS FALSE
      AND volume_data_gb IS NOT NULL
      AND offer_type_clean <> 'ligne_speciale'
      AND price_eur > 0
),

calcul_pays AS (
    SELECT
        pays,
        offer_type,
        
        -- cout median du gb  

        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY price_month_eur / NULLIF(volume_month_data, 0)
        )::numeric, 3) AS cout_go_median_eur,
        
        -- prix mensuel 
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY price_month_eur
        )::numeric, 2) AS prix_median_mensuel_eur,
        
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY volume_month_data
        )::numeric, 2) AS volume_median_go,
        
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY (price_month_eur / NULLIF(estimated_monthly_income_eur, 0)) * 100
        )::numeric, 2) AS dai_mediane_pct,
        
        
        ROUND(AVG(price_month_eur)::numeric, 2) AS prix_moyen_mensuel_eur,
        ROUND(AVG(volume_month_data)::numeric, 2) AS volume_mensuel_moyen_gb,
        
        -- cout du gb en euro 

        ROUND((SUM(price_month_eur) / NULLIF(SUM(volume_month_data), 0))::numeric, 3) AS cout_gb_moyen_eur,
        
        ROUND(AVG((price_month_eur / NULLIF(estimated_monthly_income_eur, 0)) * 100)::numeric, 2) AS dai_moyen_pct,
        
        COUNT(*) AS nb_offres

    FROM resume_pays
    GROUP BY pays, offer_type 
)

SELECT *
FROM calcul_pays
ORDER BY cout_go_median_eur ASC