import { Fyo } from 'fyo';
import { FrappeDatabaseDemux } from 'src/web/databaseDemux';

export const fyo = new Fyo({
  DatabaseDemux: FrappeDatabaseDemux,
});
