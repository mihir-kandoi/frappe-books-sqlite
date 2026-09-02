import { Fyo } from 'fyo';
import { FrappeDatabaseDemux } from 'src/web/databaseDemux';

/**
 * Global fyo: this is meant to be used only by the app. For
 * testing purposes a separate instance of fyo should be initialized.
 */

const isElectron = typeof ipc !== 'undefined';

export const fyo = new Fyo({
  isTest: false,
  isElectron,
  DatabaseDemux: isElectron ? undefined : FrappeDatabaseDemux,
});
