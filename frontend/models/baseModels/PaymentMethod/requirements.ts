import { PaymentMethodType } from 'models/types';

export type PaymentMethodRequirements = {
  isCash: boolean;
  requiresReferenceId: boolean;
  requiresClearanceDate: boolean;
};

export function getPaymentMethodRequirements(
  type?: PaymentMethodType,
  requiresClearanceDate = false
): PaymentMethodRequirements {
  const isCash = type === 'Cash';

  return {
    isCash,
    requiresReferenceId: Boolean(type && !isCash),
    requiresClearanceDate: Boolean(requiresClearanceDate),
  };
}
