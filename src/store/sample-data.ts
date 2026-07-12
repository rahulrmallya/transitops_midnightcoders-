import type { Driver, Vehicle } from "@/types";

export const vehicles: Vehicle[] = [
  { id: "V-1001", name: "Tata Ace Gold", registration: "KA-01-AB-4521", type: "Mini Truck", capacity: "750 kg", odometer: 48210, status: "Available", lastActivity: "2h ago · Depot A" },
  { id: "V-1002", name: "Ashok Leyland Dost+", registration: "KA-05-CJ-1187", type: "Light Truck", capacity: "1.25 T", odometer: 91340, status: "On Trip", lastActivity: "En route · Hosur" },
  { id: "V-1003", name: "Mahindra Bolero Pickup", registration: "KA-03-MN-7742", type: "Pickup", capacity: "1.7 T", odometer: 62110, status: "In Maintenance", lastActivity: "Service Bay 2" },
  { id: "V-1004", name: "Eicher Pro 2049", registration: "KA-09-EF-2210", type: "Medium Truck", capacity: "4 T", odometer: 118450, status: "Available", lastActivity: "1h ago · Depot B" },
  { id: "V-1005", name: "BharatBenz 1015R", registration: "KA-04-BH-9931", type: "Heavy Truck", capacity: "10 T", odometer: 204880, status: "On Trip", lastActivity: "En route · Chennai" },
  { id: "V-1006", name: "Tata Intra V30", registration: "KA-07-IT-3345", type: "Compact Truck", capacity: "1.3 T", odometer: 32100, status: "Available", lastActivity: "30m ago · Depot A" },
  { id: "V-1007", name: "Mahindra Furio 7", registration: "KA-02-MF-6612", type: "Medium Truck", capacity: "7 T", odometer: 87220, status: "Retired", lastActivity: "Retired 12 Mar" },
  { id: "V-1008", name: "Ashok Leyland Ecomet", registration: "KA-06-EC-4408", type: "Medium Truck", capacity: "5 T", odometer: 143005, status: "In Maintenance", lastActivity: "Service Bay 4" },
  { id: "V-1009", name: "Eicher Pro 3015", registration: "KA-08-EP-8890", type: "Heavy Truck", capacity: "9 T", odometer: 176420, status: "On Trip", lastActivity: "En route · Mangalore" },
  { id: "V-1010", name: "Tata 407 LPT", registration: "KA-10-LP-2276", type: "Light Truck", capacity: "2.5 T", odometer: 99870, status: "Available", lastActivity: "20m ago · Depot C" },
];

export const drivers: Driver[] = [
  { id: "D-2001", name: "Rakesh Gowda",   phone: "+91 98450 11223", email: "rakesh.g@transitops.in",  licenceNumber: "KA0120180012345", category: "HMV", licenceExpiry: "2027-06-14", licenceStatus: "Valid", safetyScore: 92, safetyBand: "High", status: "On Trip" },
  { id: "D-2002", name: "Suresh Patil",   phone: "+91 98861 44210", email: "suresh.p@transitops.in",  licenceNumber: "KA0520170087721", category: "HMV", licenceExpiry: "2026-02-03", licenceStatus: "Valid", safetyScore: 88, safetyBand: "High", status: "Available" },
  { id: "D-2003", name: "Imran Sheikh",   phone: "+91 97400 55631", email: "imran.s@transitops.in",   licenceNumber: "KA0320190045512", category: "LMV", licenceExpiry: "2025-12-22", licenceStatus: "Expiring Soon", safetyScore: 76, safetyBand: "Medium", status: "Available" },
  { id: "D-2004", name: "Manjunath Rao",  phone: "+91 96320 90012", email: "manju.r@transitops.in",   licenceNumber: "KA0420160091143", category: "HMV", licenceExpiry: "2024-11-05", licenceStatus: "Expired", safetyScore: 61, safetyBand: "Low", status: "Suspended" },
  { id: "D-2005", name: "Anil Kumar",     phone: "+91 99012 33445", email: "anil.k@transitops.in",    licenceNumber: "KA0720180022998", category: "LMV", licenceExpiry: "2028-01-19", licenceStatus: "Valid", safetyScore: 95, safetyBand: "High", status: "On Trip" },
  { id: "D-2006", name: "Prakash Naik",   phone: "+91 90080 21114", email: "prakash.n@transitops.in", licenceNumber: "KA0620190066120", category: "HMV", licenceExpiry: "2026-08-28", licenceStatus: "Valid", safetyScore: 82, safetyBand: "High", status: "Off Duty" },
  { id: "D-2007", name: "Vinay Shetty",   phone: "+91 98801 77452", email: "vinay.s@transitops.in",   licenceNumber: "KA0820170034421", category: "LMV", licenceExpiry: "2025-10-30", licenceStatus: "Expiring Soon", safetyScore: 70, safetyBand: "Medium", status: "Available" },
  { id: "D-2008", name: "Basavraj Hiremath", phone: "+91 94480 66330", email: "basav.h@transitops.in", licenceNumber: "KA0220180099210", category: "HMV", licenceExpiry: "2027-03-12", licenceStatus: "Valid", safetyScore: 90, safetyBand: "High", status: "On Trip" },
  { id: "D-2009", name: "Ravi Teja",      phone: "+91 91480 22105", email: "ravi.t@transitops.in",    licenceNumber: "KA0920200011098", category: "LMV", licenceExpiry: "2026-05-06", licenceStatus: "Valid", safetyScore: 78, safetyBand: "Medium", status: "Available" },
  { id: "D-2010", name: "Nagaraj Bhat",   phone: "+91 90350 88771", email: "nagaraj.b@transitops.in", licenceNumber: "KA1020160073350", category: "HMV", licenceExpiry: "2025-01-11", licenceStatus: "Expired", safetyScore: 58, safetyBand: "Low", status: "Off Duty" },
];

export const fleetUtilization = [
  { month: "Jan", utilization: 62 },
  { month: "Feb", utilization: 65 },
  { month: "Mar", utilization: 71 },
  { month: "Apr", utilization: 68 },
  { month: "May", utilization: 74 },
  { month: "Jun", utilization: 77 },
  { month: "Jul", utilization: 82 },
  { month: "Aug", utilization: 78 },
  { month: "Sep", utilization: 80 },
];

export const vehicleStatusMix = [
  { name: "Available", value: 84, key: "available" },
  { name: "On Trip", value: 24, key: "ontrip" },
  { name: "Maintenance", value: 9, key: "maintenance" },
  { name: "Retired", value: 11, key: "retired" },
];

export const operationalActivity = [
  { day: "Mon", trips: 34, fuel: 28 },
  { day: "Tue", trips: 42, fuel: 31 },
  { day: "Wed", trips: 39, fuel: 30 },
  { day: "Thu", trips: 47, fuel: 34 },
  { day: "Fri", trips: 52, fuel: 38 },
  { day: "Sat", trips: 45, fuel: 33 },
  { day: "Sun", trips: 22, fuel: 18 },
];

export const recentActivity = [
  { id: 1, title: "Trip TRP-8842 completed", meta: "Ashok Leyland Dost+ · 2h ago", tone: "success" as const },
  { id: 2, title: "Maintenance scheduled", meta: "Eicher Pro 2049 · Bay 3 · 3h ago", tone: "warning" as const },
  { id: 3, title: "Driver Anil Kumar started trip", meta: "Bengaluru → Mysuru · 4h ago", tone: "info" as const },
  { id: 4, title: "Fuel refill logged", meta: "Tata Ace Gold · ₹4,220 · 5h ago", tone: "brand" as const },
  { id: 5, title: "Licence expiring soon", meta: "Imran Sheikh · 22 Dec · 6h ago", tone: "warning" as const },
  { id: 6, title: "Vehicle returned to depot", meta: "Tata 407 LPT · Depot C · 7h ago", tone: "success" as const },
];

export const fleetHealth = [
  { label: "Vehicles healthy", value: 108, tone: "success" as const },
  { label: "Service due (7d)", value: 12, tone: "warning" as const },
  { label: "Critical alerts", value: 3, tone: "destructive" as const },
  { label: "Idle > 24h", value: 5, tone: "info" as const },
];
