-- disable bncr payment provider
UPDATE payment_provider
   SET bncr_commerce_id = NULL,
       bncr_secret_key = NULL;
