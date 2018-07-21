-- Should return two successful tests and one failing test
BEGIN;
    SELECT plan(3);
    SELECT has_column('whatever.contact', 'name', 'contacts should have a name');
    SELECT fail('simple fail');
    SELECT pass('simple pass');
    SELECT * FROM finish();
ROLLBACK;
