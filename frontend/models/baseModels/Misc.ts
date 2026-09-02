import { Doc } from 'fyo/model/doc';
import { HiddenMap } from 'fyo/model/types';

export class Misc extends Doc {
  useFullWidth?: boolean;
  override hidden: HiddenMap = {};
}
