CREATE VIEW DailyTagSpend AS SELECT jsonb_array_elements_text(s.request_tags) AS individual_request_tag,
    date(s."startTime") AS spend_date,
    count(*) AS log_count,
    sum(s.spend) AS total_spend
   FROM "LiteLLM_SpendLogs" s
  GROUP BY (jsonb_array_elements_text(s.request_tags)), (date(s."startTime"));

CREATE OR REPLACE VIEW DailyTagSpend AS
SELECT 
  COALESCE(tag, '[无标签]') AS individual_request_tag,
  date(s."startTime") AS spend_date,
  COUNT(*) AS log_count,
  SUM(s.spend) AS total_spend
FROM "LiteLLM_SpendLogs" s
LEFT JOIN LATERAL jsonb_array_elements_text(s.request_tags) AS t(tag) ON true
GROUP BY tag, spend_date;

SELECT 
    u.user_email AS user_email,
    COUNT(s."user") AS request_count
FROM "LiteLLM_SpendLogs" s
JOIN "LiteLLM_UserTable" u 
    ON s."user" = u.user_id::text  -- 注意类型转换（假设user_id是UUID类型）
WHERE 
    s."startTime" > '2025-02-13' 
GROUP BY 
    u.user_email, s."user"  -- 双字段分组确保准确性
ORDER BY 
    1 DESC;