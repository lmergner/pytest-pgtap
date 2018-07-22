-- Copyright (c) 2018 Luke Mergner and contributors
-- Should return raise a bad plan warning
BEGIN;
    SELECT plan(1);
    SELECT has_column('whatever.contact', 'name', 'contacts should have a name');
    SELECT fail('simple fail');
    SELECT pass('simple pass');
    SELECT * FROM finish();
ROLLBACK;