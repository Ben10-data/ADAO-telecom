with union_table as (
    
    {{ dbt_utils.union_relations(
        relations=[
            source('telecom', 'comores_tel'),
            source('telecom', 'comores_yas'),
            source('telecom', 'mada_yas'),
            source('telecom', 'myt_mau'),
            source('telecom', 'sen_yas'),
            source('telecom', 'tanza_yas')
        ]
    ) }}

), 
Avec_pays_context as (

        SELECT u.*, 
            c.*
        FROM union_table as u
        LEFT JOIN {{ source('telecom', 'context_pays') }} c
        ON LOWER(TRIM(u.country)) = LOWER(TRIM(c.country_name))

),

avant_final AS (

    SELECT
        *,
        CASE
            WHEN UPPER(TRIM(currency)) = 'KMF'
                THEN ROUND(price_local / 491.96775, 2)
            WHEN UPPER(TRIM(currency)) = 'XOF'
                THEN ROUND(price_local / 655.957, 2)
            WHEN UPPER(TRIM(currency)) = 'MGA'
                THEN ROUND(price_local/ 5000.0, 2)
            WHEN UPPER(TRIM(currency)) = 'TZS'
                THEN ROUND(price_local / 3000.0, 2)
            WHEN UPPER(TRIM(currency)) = 'RS'
                THEN ROUND(price_local / 50.0, 2)
            ELSE NULL
        END AS price_eur

    FROM avec_pays_context

),

income_calc AS (

    SELECT
        *,
        ROUND(data_volume_gb::numeric, 2) as volume_data_gb,
        (estimated_monthly_income_usd / 1.08) AS estimated_monthly_income_eur
    FROM avant_final

),

media_clean as (
    SELECT *,

    CASE 
        WHEN offer_type='home_5g' THEN 'fixed_wireless'
        WHEN offer_type in ('fiber_pro', 'fibre') THEN 'fiber'
        ELSE offer_type
    END as offer_type_clean,        

    CASE
        WHEN media_type = '4G+/5G' 
            THEN '4G/5G'
        WHEN media_type='fibre'
            THEN 'fiber'
        WHEN media_type = 'mobile_data' THEN 'mobile'
        ELSE media_type
    END as media_type_clean

    FROM income_calc
),

final AS (

    SELECT
        *,

        CASE
            WHEN data_volume_gb > 0
            THEN ROUND((price_eur / NULLIF(data_volume_gb,0))::numeric, 3)
            ELSE NULL
        END AS cost_per_gb_eur,

        CASE
            WHEN estimated_monthly_income_eur > 0
                 AND price_eur > 0
            THEN ROUND(((price_eur / estimated_monthly_income_eur) * 100)::numeric, 2)
            ELSE NULL
        END AS dai_pct

    FROM media_clean
)

select * from final 