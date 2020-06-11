function dydt = morotti_et_al_mouse_camkiiODEfile(t,y,p)
% This function computes the CaMKII-dependent phosphorylation profiles for
% LTCCs (dyadic and subsarcolemmal), RyRs, and PLB. 

%% Description of state variables

% LCCp-PKA = y(1);        % [LCCp] by PKA (currently unused anywhere else)
% LCCp-CaMKIIdyad = y(2); % Dyadic [LCCp] by dyadic CaMKII
% RyR-Ser2809p = y(3);    % [RyR-Ser2809p] by PKA (currently unused anywhere else)
% RyR-Ser2815p = y(4);    % [RyR-Ser2815p] by CaMKII 
% PLB-Thr17p = y(5);      % [PLB-Thr17p] by CaMKII
% LCCp-CaMKIIsl = y(6);   % Subsarcolemmal [LCCp] by subsarcolemmal CaMKII
%% RATE CONSTANTS and KM VALUES

% L-Type Ca Channel (LTCC) parameters
k_ckLCC = 0.4;                  % [s^-1]
k_pp1LCC = 0.1103;              % [s^-1] 
k_pkaLCC = 13.5;                % [s^-1] 
k_pp2aLCC = 10.1;               % [s^-1] 

KmCK_LCC = 12;                  % [uM] 
KmPKA_LCC = 21;                 % [uM] 
KmPP2A_LCC = 47;                % [uM] 
KmPP1_LCC = 9;                  % [uM] 

% Ryanodine Receptor (RyR) parameters
k_ckRyR = 0.4;                  % [s^-1] 
k_pkaRyR = 1.35;                % [s^-1] 
k_pp1RyR = 1.07;                % [s^-1] 
k_pp2aRyR = 0.481;              % [s^-1] 

% Basal RyR phosphorylation (numbers based on param estimation)
kb_2809 = 0.51;                 % [uM/s] - PKA site
kb_2815 = 0.35;                 % [uM/s] - CaMKII site

KmCK_RyR = 12;                  % [uM] 
KmPKA_RyR = 21;                 % [uM] 
KmPP1_RyR = 9;                  % [uM] 
KmPP2A_RyR = 47;                % [uM] 

% Phospholamban (PLB) parameters
k_ckPLB = 8e-3;                 % [s^-1]
k_pp1PLB = .0428;               % [s^-1]

KmCK_PLB = 12;
KmPP1_PLB = 9;

% Okadaic Acid inhibition params (based on Huke/Bers [2008])
% Want to treat OA as non-competitive inhibitor of PP1 and PP2A
Ki_OA_PP1 = 0.78;        % [uM] - Values from fit
Ki_OA_PP2A = 0.037;      % [uM] - Values from fit
%% Assign input params and y0s

paramsCell=mat2cell(p,ones(size(p,1),1),ones(size(p,2),1));
[CaMKIIactDyad,LCCtotDyad,RyRtot,PP1_dyad,PP2A_dyad,OA,PLBtot,...
 CaMKIIactSL,LCCtotSL,PP1_SL,PP1_PLB_avail] = paramsCell{:};

yCell=mat2cell(y,ones(size(y,1),1),ones(size(y,2),1));
[LCC_PKAp,LCC_CKdyadp,RyR2809p,RyR2815p,PLBT17p,LCC_CKslp] = yCell{:};

% Default PKA level
PKAc = 95.6*.54;
%% OA inhibition term (non-competitive) for PP1 and PP2A

OA_PP1 = 1/(1 + (OA/Ki_OA_PP1)^3);
OA_PP2A = 1/(1 + (OA/Ki_OA_PP2A)^3);

%% ODE EQUATIONS

% LTCC states (note: PP2A is acting on PKA site and PP1 on CKII site)
% CaMKII phosphorylation of Dyadic LCCs
LCC_CKdyadn = LCCtotDyad - LCC_CKdyadp;
LCCDyad_PHOS = (k_ckLCC*CaMKIIactDyad*LCC_CKdyadn)/(KmCK_LCC+LCC_CKdyadn);
LCCDyad_DEPHOS = (k_pp1LCC*PP1_dyad*LCC_CKdyadp)/(KmPP1_LCC+LCC_CKdyadp)*OA_PP1;
dLCC_CKdyadp = LCCDyad_PHOS - LCCDyad_DEPHOS;

% CaMKII phosphorylation of Sub-sarcolemmal LCCs
LCC_CKsln = LCCtotSL - LCC_CKslp;
LCCSL_PHOS = (k_ckLCC*CaMKIIactSL*LCC_CKsln)/(KmCK_LCC+LCC_CKsln); 
LCCSL_DEPHOS = (k_pp1LCC*PP1_SL*LCC_CKslp)/(KmPP1_LCC+LCC_CKslp)*OA_PP1;
dLCC_CKslp = LCCSL_PHOS - LCCSL_DEPHOS; 

% PKA phosphorylation (currently unused elsewhere)
LCC_PKAn = LCCtotDyad - LCC_PKAp;
dLCC_PKAp = (k_pkaLCC*PKAc*LCC_PKAn)/(KmPKA_LCC+LCC_PKAn) - ...
            (k_pp2aLCC*PP2A_dyad*LCC_PKAp)/(KmPP2A_LCC+LCC_PKAp)*OA_PP2A;
% RyR states
RyR2815n = RyRtot - RyR2815p;
RyR_BASAL = kb_2815*RyR2815n;
RyR_PHOS = (k_ckRyR*CaMKIIactDyad*RyR2815n)/(KmCK_RyR+RyR2815n);
RyR_PP1_DEPHOS = (k_pp1RyR*PP1_dyad*RyR2815p)/(KmPP1_RyR+RyR2815p)*OA_PP1;
RyR_PP2A_DEPHOS = (k_pp2aRyR*PP2A_dyad*RyR2815p)/(KmPP2A_RyR+RyR2815p)*OA_PP2A;
dRyR2815p = RyR_BASAL + RyR_PHOS - RyR_PP1_DEPHOS - RyR_PP2A_DEPHOS;

% PKA phosphorylation of Ser 2809 on RyR (currently unused elsewhere)
RyR2809n = RyRtot - RyR2809p;
dRyR2809p = kb_2809*RyR2809n + (k_pkaRyR*PKAc*RyR2809n)/(KmPKA_RyR+RyR2809n) - ...
            (k_pp1RyR*PP1_dyad*RyR2809p)/(KmPP1_RyR+RyR2809p)*OA_PP1;        

% PLB states
PP1_PLB = PP1_dyad*PP1_PLB_avail; % Inhibitor-1 regulation of PP1_dyad included here
PLBT17n = PLBtot - PLBT17p;
PLB_PHOS = (k_ckPLB*PLBT17n*CaMKIIactDyad)/(KmCK_PLB+PLBT17n);
PLB_DEPHOS = (k_pp1PLB*PP1_PLB*PLBT17p)/(KmPP1_PLB+PLBT17p)*OA_PP1;
dPLBT17p = PLB_PHOS - PLB_DEPHOS; 

%% Collect ODEs and convert to uM/ms
dydt = [dLCC_PKAp; 
        dLCC_CKdyadp;
        dRyR2809p; 
        dRyR2815p;
        dPLBT17p; 
        dLCC_CKslp].*10^-3;  % Convert to uM/ms
    
% CaMKII clamp: set dy/dt=0 % dydt = [0;0;0;0;0;0];