BEGIN;
    SELECT plan(1);
    SELECT has_column('whatever.contact', 'name', 'contacts should have a name');
    SELECT pass('simple pass');
    SELECT * FROM finish();
ROLLBACK;