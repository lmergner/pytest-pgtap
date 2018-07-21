-- Should return two successful tests
BEGIN;
    SELECT plan(2);
    SELECT has_column('whatever.contact', 'name', 'contacts should have a name');
    SELECT pass('simple pass');
    SELECT * FROM finish();
ROLLBACK;
