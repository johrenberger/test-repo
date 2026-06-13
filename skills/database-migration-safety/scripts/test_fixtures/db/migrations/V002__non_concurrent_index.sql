-- Test fixture: should trigger create_index_non_concurrent pattern
CREATE INDEX idx_user_email ON users(email);
