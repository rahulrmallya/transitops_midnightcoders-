export type VehicleStatus = "Available" | "On Trip" | "In Maintenance" | "Retired";

export interface Vehicle {
  id: string;
  name: string;
  registration: string;
  type: string;
  capacity: string;
  odometer: number;
  status: VehicleStatus;
  lastActivity: string;
}

export type DriverStatus = "Available" | "On Trip" | "Off Duty" | "Suspended";
export type LicenceStatus = "Valid" | "Expiring Soon" | "Expired";
export type SafetyBand = "High" | "Medium" | "Low";

export interface Driver {
  id: string;
  name: string;
  phone: string;
  email: string;
  licenceNumber: string;
  category: string;
  licenceExpiry: string;
  licenceStatus: LicenceStatus;
  safetyScore: number;
  safetyBand: SafetyBand;
  status: DriverStatus;
}
