function ydot = morotti_et_al_mouse_eccODEfile(t,y,p)
% This file describes the EC coupling starting from the framework of the
% Shannon-Bers model of rabbit ventricular EC coupling.
% Reference: Shannon TR, Wang F, Puglisi J, Weber C & Bers DM. (2004).
% A mathematical treatment of integrated Ca dynamics within the
% ventricular myocyte. Biophysical Journal 87, 3351-3371.

% get the stimulation protocol passed from main.m
StimProtocol = p(end);
p = p(1:end-1);
%% Assign passed-in parameters

cycleLength = p(1);
% CaMKII phosphorylated targets (%)
LCC_CKp = p(2);
RyR_CKp = p(3);
PLB_CKp = p(4);
% PKA phosphorylated targets (%)
LCCa_PKAp = p(5);
LCCb_PKAp = p(6);
PLB_PKAn = p(7); % This is % non-phosphorylated PLB targets
RyR_PKAp = p(8);
TnI_PKAp = p(9);
IKs_PKAp = p(10); % not present in MOUSE
ICFTR_PKAp = p(11); % not present in MOUSE
IKur_PKAp = p(16); % MOUSE
PLM_PKAp = p(17); % MOUSE
% Flag for CaMKII-OE
CKIIOE = p(12);
% Protocol parameters
rest = p(13);
variablePar = p(14);
% PKA
Ligtot = p(15);

ydot = zeros(size(y));
%% Flags

% Protocol
if StimProtocol == 0
    protocol = 'pace_hr_control';
elseif StimProtocol == 1
    protocol = 'AP_clamp_hr_control';
else
    disp(['Invalid choice of stimulation protocol: only 0 or 1 accepted '...
        'for pace hr or current clamp control, respectively']);
end

% protocol = 'AP_clamp_hr_control';

% Set CKIIflag to 1 for CaMKII-OE, 0 otherwise
CKIIflag = CKIIOE;
% Set ICa_MarkovFlag to 1 for Markov ICa, 0 otherwise
ICa_MarkovFlag = 1;
% Set INa_MarkovFlag to 1 for Markov INa, 0 otherwise
INa_MarkovFlag = 0;
% Set Ito to use either origl params (=0) or Grandi Params (=1)
ItoFlag = 1;

% Na clamp (set flag to 1, 0 otherwise)
NaClampFlag = 0;
% PLM KO (set flag to 1, 0 otherwise)
PLMkoFlag = 0;
% Strophanthidin (dyastolic Na influx) (set flag to 1, 0 otherwise)
StrophFlag = 0;
% Caffeine-induced Ca transient (set flag to 1, 0 otherwise)
CaffeineFlag = 0;
% Digitalis (set flag to 1, 0 otherwise)
DigitalisFlag = 0;
%% Na loading and CaMKII-Na-Ca-CaMKII loop properties

% Na loading parameters ON (set flag to 1, 0 otherwise)
NaGainFlag=0; % WT (default 0)
if CKIIflag==1,
    NaGainFlag=1; % CaMKII-OE (default 1)
end

% CaMKII-Na-Ca-CaMKII loop closed (set flag to 1, 0 otherwise)
loop = 0; % (default 0)
%% Model Parameters

% Constants
R = 8314;       % [J/kmol*K]  
Frdy = 96485;   % [C/mol]  
Temp = 310;     % [K] 310 K (37 C) for BT / 295 K (22 C) for RT
FoRT = Frdy/R/Temp;
Qpow = (Temp-310)/10;

% Cell geometry
Acell = 20e3; % [um^2] MOUSE
%Cmem = 1.3810e-10; % [F] membrane capacitance RABBIT
Cmem = Acell*1e-14; % [F] 200 pF membrane capacitance MOUSE

% Fractional currents in compartments
%Fjunc = 0.11; Fsl = 1-Fjunc; % RABBIT
%Fjunc = 0.3; Fsl = 1-Fjunc; % MOUSE
Fjunc = 17/(17+31)*7/17+31/(17+31)*2/31; Fsl = 1-Fjunc; % MOUSE Fjunc = 0.1875;
%Fjunc_nak = Fjunc; Fsl_nak = 1-Fjunc_nak; % RABBIT
Fjunc_nak = 1.6*17/(1.6*17+31)*7/17+31/(1.6*17+31)*2/31; Fsl_nak = 1-Fjunc_nak; % MOUSE Fjunc = 0.2268;
Fjunc_ncx = Fjunc; Fsl_ncx = 1-Fjunc_ncx;
%Fjunc_ncx = Fjunc_nak; Fsl_ncx = 1-Fjunc_ncx;
%Fjunc_ncx = 0.5; Fsl_ncx = 1-Fjunc_ncx;
%Fjunc_ncx = 0.9; Fsl_ncx = 1-Fjunc_ncx;
Fjunc_CaL = 0.9; Fsl_CaL = 1-Fjunc_CaL;

cellLength = 100; % cell length [um]
cellRadius = 10.25; % cell radius [um]
junctionLength = 15e-3; % junc length [um]
junctionRadius = 160e-3; % junc radius [um]
distSLcyto = 0.45; % dist. SL to cytosol [um]
%distJuncSL = 0.5; % dist. junc to SL [um] RABBIT
distJuncSL = 0.3; % dist. junc to SL [um] MOUSE
DcaJuncSL = 1.64e-6; % Dca junc to SL [cm^2/sec]
DcaSLcyto = 1.22e-6; % Dca SL to cyto [cm^2/sec]
DnaJuncSL = 1.09e-5; % Dna junc to SL [cm^2/sec]
DnaSLcyto = 1.79e-5; % Dna SL to cyto [cm^2/sec] 
Vcell = pi*cellRadius^2*cellLength*1e-15; % [L]
Vmyo = 0.65*Vcell; Vsr = 0.035*Vcell; Vsl = 0.02*Vcell; Vjunc = 0.0539*.01*Vcell; 
%SAjunc = 20150*pi*2*junctionLength*junctionRadius; % [um^2] RABBIT
%SAsl = pi*2*cellRadius*cellLength % [um^2] RABBIT
SAsl = Fsl*Acell; % [um^2]  MOUSE
Njunc = (Fjunc*Acell)/(pi*junctionRadius^2); % [-]
SAjunc = Njunc*pi*2*junctionLength*junctionRadius; % [um^2] MOUSE
%spacing=sqrt(2*Acell/Njunc); % [um] not used -> reduction in distJuncSL

%J_ca_juncsl = 1/1.2134e12; % [L/msec] [m^2/sec] RABBIT
%J_ca_slmyo = 1/2.68510e11; % RABBIT
%J_na_juncsl = 1/(1.6382e12/3*100); % RABBIT 
%J_na_slmyo = 1/(1.8308e10/3*100);  % RABBIT 
J_ca_juncsl = DcaJuncSL*SAjunc/distJuncSL*1e-10; % [L/msec] [m^2/sec] MOUSE
J_ca_slmyo = DcaSLcyto*SAsl/distSLcyto*1e-10; % MOUSE
J_na_juncsl = DnaJuncSL*SAjunc/distJuncSL*1e-10; % MOUSE
J_na_slmyo = DnaSLcyto*SAsl/distSLcyto*1e-10; % MOUSE

% Fixed ion concentrations     
Cli = 15;   % Intracellular Cl  [mM]
Clo = 150;  % Extracellular Cl  [mM]
Ko = 5.4;   % Extracellular K   [mM]
Nao = 140;  % Extracellular Na  [mM]
Cao = 1;    % Extracellular Ca  [mM] MOUSE % 1.8 mM in RABBIT
Mgi = 1;    % Intracellular Mg  [mM]

% Nernst Potentials
ena_junc = (1/FoRT)*log(Nao/y(32));     % [mV]
ena_sl = (1/FoRT)*log(Nao/y(33));       % [mV]
ek = (1/FoRT)*log(Ko/y(35));	        % [mV]
eca_junc = (1/FoRT/2)*log(Cao/y(36));   % [mV]
eca_sl = (1/FoRT/2)*log(Cao/y(37));     % [mV]
ecl = (1/FoRT)*log(Cli/Clo);            % [mV]
%% Na transport parameters

GNa = 10; % [mS/uF] changed from rabbit (16)
GNaB = 4.5*0.297e-3; % [mS/uF] changed from rabbit

IbarNaK = 5; % [uA/uF] changed from rabbit (1.90719)
if NaGainFlag == 1,
    GNaB=GNaB*4;
    IbarNaK=IbarNaK*0.9;
end
if DigitalisFlag == 1,
    IbarNaK = IbarNaK*0.5; % 50% block
end
KmNaip = 19; % [mM] changed from rabbit (11)
KmKo = 1.5; % [mM]
Q10NaK = 1.63;
Q10KmNai = 1.39;
if PLMkoFlag==1,
    PLM_PKAp=1;
    GNaB=GNaB*48/20;
    IbarNaK=IbarNaK*0.8;
end
if StrophFlag==1,
    IbarNaK = 0;
end

% INa Markov Model parameters
GNa2 = 10.64;%23;      % [mS/uF]

P1a1=3.802;
P2a1=0.1027;
P3a1=2.5;
P4a1=17;
P5a1=0.20;
P6a1=150;
P4a2=15;
P5a2=0.23;
P4a3=12;
P5a3=0.25;
P1b1=0.1917;
P2b1=20.3;
P1b2=0.2;
P2b2=2.5;
P1b3=0.22;
P2b3=7.5;
P1a4=0.188495;
P2a4=16.6;
P3a4=0.393956;
P4a4=7;
P1a5=7e-7;
P2a5=7.2; % TG 7.8
P1b5=0.0044; % TG 0.00467
P2b5=2e-5;
P1a6=100;
P1b6=8.9554e-7; % TG 6.5449e-7
P2b6=11.3944;
P1a7=0.487e-4; % TG 0.3377e-3
P2a7=23.2696;
P1b7=0.2868e-3; % TG 1.868e-4
P2b7=35.9898;
P1a8=0.1e-7; % TG 6.5e-6
P1b8=9.8e-3; % TG 3.8e-3
if CKIIflag == 1, % MOUSE - CaMKII-OE
    P2a5=7.8;
    P1b5=0.00467;
    P1b6=6.5449e-7;
    P1a7=0.3377e-3;
    P1b7=1.868e-4;
    P1a8=6.5e-6;
    P1b8=3.8e-3;
end
%% K currents parameters

Kcoeff = 1; % K current modulation

pNaK = 0.01833;
GtoSlow = 0; % [mS/uF] changed from rabbit (0.06): NO ItoSlow in MOUSE
GtoFast = 0.44; % [mS/uF] changed from rabbit (0.02)
if CKIIflag == 1, % MOUSE
    GtoFast=GtoFast*2/3; % chronic CaMKII-OE effect
end
%Gkur = 0.3; % [mS/uF] only in MOUSE
    Gkur1 = 1.1*0.16; % fast
    Gkur2 = 0.14; % slow
Gss = 0.15; % [mS/uF] only in MOUSE
gkr = 0.03*sqrt(Ko/5.4);
gkp = 0.001;

% Cl current parameters
GClCa = 0.109625; % [mS/uF]
GClB = 9e-3; % [mS/uF]
KdClCa = 100e-3; % [mM]
%% LTCC parameters

K_Ica = 1.65; % MOUSE
pNa = K_Ica*1.5e-8; % [cm/sec]
pCa = K_Ica*5.4e-4; % [cm/sec] - Ca permeability
pK = K_Ica*2.7e-7; % [cm/sec]
KmCa = 0.6e-3; % [mM]
Q10CaL = 1.8; 
%% Ca transport parameters

IbarNCX = 1; % [uA/uF] changed from rabbit (9)
if CKIIflag == 1,
    IbarNCX = 1.5*IbarNCX;
end
KmCai = 3.59e-3;    % [mM]
KmCao = 1.3;        % [mM]
KmNai = 12.29;      % [mM]
KmNao = 87.5;       % [mM]
ksat = 0.27;        % [none]  
nu = 0.35;          % [none]
Kdact = 1/2*0.256e-3; % [mM] changed from rabbit
Q10NCX = 1.57;      % [none]
IbarSLCaP = 0.0673; % [uA/uF]
KmPCa = 0.5e-3;     % [mM]
GCaB = 3*2.513e-4; % [uA/uF] changed from rabbit (2.513e-4)
Q10SLCaP = 2.35;    % [none]

% SR flux parameters
Q10SRCaP = 2.6;          % [none]
Vmax_SRCaP = 1.15*1.15*2.86e-4; % [mM/msec] (mmol/L cytosol/msec) changed
Kmf = 0.3e-3; % [mM] changed from rabbit (0.246e-3) % from Yang-Saucerman
Kmr = 2.1; % [mM]L cytosol changed from rabbit (1.7) % from Yang-Saucerman
hillSRCaP = 1.787;       % [mM]
ks = 25;                 % [1/ms]      
koCa = 10;               % [mM^-2 1/ms]
kom = 0.06;              % [1/ms]     
kiCa = 0.5;              % [1/mM/ms]
kim = 0.005;             % [1/ms]
ec50SR = 0.45+0.05;      % [mM] changed from rabbit (0.45)

if CaffeineFlag==1,
    koCa=koCa*7.5;
    GCaB=0;
    Vmax_SRCaP=0;
end
%% Buffering parameters

Bmax_Naj = 7.561;       % [mM] 
Bmax_Nasl = 1.65;       % [mM]
koff_na = 1e-3;         % [1/ms]
kon_na = 0.1e-3;        % [1/mM/ms]
Bmax_TnClow = 70e-3;    % [mM]                      % TnC low affinity
koff_tncl = 19.6e-3;    % [1/ms] 
kon_tncl = 32.7;        % [1/mM/ms]
Bmax_TnChigh = 140e-3;  % [mM]                      % TnC high affinity 
koff_tnchca = 0.032e-3; % [1/ms] 
kon_tnchca = 2.37;      % [1/mM/ms]
koff_tnchmg = 3.33e-3;  % [1/ms] 
kon_tnchmg = 3e-3;      % [1/mM/ms]
Bmax_myosin = 140e-3;   % [mM]                      % Myosin buffering
koff_myoca = 0.46e-3;   % [1/ms]
kon_myoca = 13.8;       % [1/mM/ms]
koff_myomg = 0.057e-3;  % [1/ms]
kon_myomg = 0.0157;     % [1/mM/ms]
Bmax_SR = 19*.9e-3;     % [mM] 
koff_sr = 60e-3;        % [1/ms]
kon_sr = 100;           % [1/mM/ms]
Bmax_SLlowsl = 37.38e-3*Vmyo/Vsl;        % [mM]    % SL buffering
Bmax_SLlowj = 4.62e-3*Vmyo/Vjunc*0.1;    % [mM]    
koff_sll = 1300e-3;     % [1/ms]
kon_sll = 100;          % [1/mM/ms]
Bmax_SLhighsl = 13.35e-3*Vmyo/Vsl;       % [mM] 
Bmax_SLhighj = 1.65e-3*Vmyo/Vjunc*0.1;  % [mM] 
koff_slh = 30e-3;       % [1/ms]
kon_slh = 100;          % [1/mM/ms]
Bmax_Csqn = 2.7;        %140e-3*Vmyo/Vsr; [mM] 
koff_csqn = 65;         % [1/ms] 
kon_csqn = 100;         % [1/mM/ms] 

% PKA-dependent phosphoregulation of TnI (increases Kd of TnC)
fracTnIpo = 0.062698;  % Derived quantity (TnI_PKAp(baseline)/TnItot)
%fPKA_TnI = (1.45-0.45*(1-TnI_PKAp)/(1-fracTnIpo)); % Max effect +45%
fPKA_TnI = (1.61-0.61*(1-TnI_PKAp)/(1-fracTnIpo)); % Max effect +61%
koff_tncl = koff_tncl*fPKA_TnI;
%% Global Variable for Time

global tStep tArray               
if t > tArray(tStep) % Roughly eliminates data from rejected time steps
    tStep = tStep + 1;  
end
tArray(tStep) = t;
%% I_Na: Fast Na Current

% Max INa alterations with CaMKII hyperactivity as in Hund & Rudy 2008
if CKIIflag == 1 % acute effects
    inashift = -3.25;
    alphaCKII = -.18;
    %deltGbarNal_CKII = 2;  % RABBIT
    if NaGainFlag == 1,
        deltGbarNal_CKII = 3;  % MOUSE
    else
        deltGbarNal_CKII = 0;  % no Na Gain in OE
    end
else
    inashift = 0;
    alphaCKII = 0;
    deltGbarNal_CKII = 0;
end

if loop == 1,
    RyRp_WT_mean=0.2101; RyRp_OE_mean=0.7387; % Derived (1 Hz, no loop)
    RyRp_OEloop_min=0.7033; % Derived (1 Hz, OE loop)
    delta_loop=(3/(RyRp_OE_mean-RyRp_WT_mean))*RyR_CKp-(3/(RyRp_OE_mean-RyRp_WT_mean))*RyRp_WT_mean;
    NaVsCaMKIIclamp=0; % if 1, CaMKII Clamp on NaV
    if NaVsCaMKIIclamp==1,
        delta_loop=(3/(RyRp_OE_mean-RyRp_WT_mean))*RyRp_OEloop_min-(3/(RyRp_OE_mean-RyRp_WT_mean))*RyRp_WT_mean;
    end
    GNaB=(4.5)*0.297e-3*(1+delta_loop);
    if CKIIflag == 1 % OE
        if NaGainFlag == 1, % acute
            deltGbarNal_CKII=delta_loop;
        else
            deltGbarNal_CKII=0;
        end
    else % WT
        deltGbarNal_CKII=0;
    end          
end

am = 0.32*(y(39)+47.13)/(1-exp(-0.1*(y(39)+47.13)));
bm = 0.08*exp(-(y(39))/11);
if (y(39)-inashift) >= -40
    ah = 0; aj = 0;
        %bh = 1/(0.13*(1+exp(-((y(39)-inashift)+10.66)/11.1))); % RABBIT
        bh = 0.66*1/(0.13*(1+exp(-((y(39)-inashift)+10.66)/11.1))); % MOUSE
    bj = 0.3*exp(-2.535e-7*(y(39)-inashift))/(1+exp(-0.1*((y(39)-inashift)+32)));
else
    ah = 0.135*exp((80+(y(39)-inashift))/-6.8);
        %bh = 3.56*exp(0.079*(y(39)-inashift))+3.1e5*exp(0.35*(y(39)-inashift)); % RABBIT
        bh = 1.1*3.56*exp(0.079*(y(39)-inashift-2))+3.1e5*exp(0.35*(y(39)-inashift-2)); % MOUSE
    % Including alteration to aj as in Hund and Rudy 2008
    aj = (1+alphaCKII)*((-1.2714e5*exp(0.2444*(y(39)-inashift))-3.474e-5*exp(-0.04391*(y(39)-inashift)))*((y(39)-inashift)+37.78)/(1+exp(0.311*((y(39)-inashift)+79.23))));
    bj = 0.1212*exp(-0.01052*(y(39)-inashift))/(1+exp(-0.1378*((y(39)-inashift)+40.14)));
end
ydot(1) = am*(1-y(1))-bm*y(1);
ydot(2) = ah*(1-y(2))-bh*y(2);
ydot(3) = aj*(1-y(3))-bj*y(3);

I_Na_junc1 = Fjunc*GNa*y(1)^3*y(2)*y(3)*(y(39)-ena_junc);
I_Na_sl1 = Fsl*GNa*y(1)^3*y(2)*y(3)*(y(39)-ena_sl);
%% I_Na,L: Late INa current (as in Hund & Rudy 2008)

GbarNal = .0065*(1+deltGbarNal_CKII)*2; % deltGbar assigned in 'Fast INa' section

% h-gate (note: m-gate is same as INa m-gate -> using y(1) for this)
hlss = 1/(1+exp((y(39)+91)/6.1));
tauhl = 600; % ms
ydot(47) = (hlss-y(47))/tauhl;
I_Nalj = Fjunc*GbarNal*y(1)^3*y(47)*(y(39)-ena_junc);
I_Nalsl = Fsl*GbarNal*y(1)^3*y(47)*(y(39)-ena_sl);
%I_Nal = I_Nalj+I_Nalsl;
%% I_Na: alternative Markov Model - unused

if INa_MarkovFlag == 1
    % State variables
    CNa2 = y(48); CNa1 = y(49); ONa = y(50); IFNa = y(51); I1Na = y(52);
    CNa3 = y(53); ICNa2 = y(54); ICNa3 = y(55); LONa = y(56);
    LCNa1 = y(57); LCNa2 = y(58); LCNa3 = y(59);
    I2Na = (1-(ONa+CNa1+CNa2+CNa3+IFNa+I1Na+ICNa2+ICNa3+LONa+LCNa1+LCNa2+LCNa3));
    % Transition rates
    alphaNa1 = P1a1/(P2a1*exp(-(y(39)+P3a1)/P4a1)+P5a1*exp(-(y(39)+P3a1)/P6a1));
    alphaNa2 = P1a1/(P2a1*exp(-(y(39)+P3a1)/P4a2)+P5a2*exp(-(y(39)+P3a1)/P6a1));
    alphaNa3 = P1a1/(P2a1*exp(-(y(39)+P3a1)/P4a3)+P5a3*exp(-(y(39)+P3a1)/P6a1));
    betaNa1 = P1b1*exp(-(y(39)+P3a1)/P2b1); % shift
    betaNa2 = P1b2*exp(-(y(39)-P2b2)/P2b1);
    betaNa3 = P1b3*exp(-(y(39)-P2b3)/P2b1);
    alphaNa4 = 1/(P1a4*exp(-(y(39)+P4a4)/P2a4)+P3a4);
    alphaNa5 = P1a5*exp(-(y(39)+P4a4)/P2a5);
    betaNa5 = (P1b5+P2b5*(y(39)+P4a4));
    betaNa6 = P1b6*exp(-y(39)/P2b6);
    alphaNa7 = P1a7*exp(y(39)/P2a7);
    betaNa7 = P1b7*exp(-y(39)/P2b7);
    alphaNa8 = P1a8;
    betaNa8 = P1b8;
        betaNa4 = (alphaNa3*alphaNa4*alphaNa5)/(betaNa3*betaNa5);
        alphaNa6 = alphaNa4/P1a6;
    % ODEs
    dCNa3  = betaNa8*LCNa3+betaNa1*CNa2+alphaNa5*ICNa3-(alphaNa1+betaNa5+alphaNa8)*CNa3;
    dCNa2  = betaNa8*LCNa2+alphaNa1*CNa3+betaNa2*CNa1+alphaNa5*ICNa2-(betaNa1+alphaNa2+betaNa5+alphaNa8)*CNa2;
    dCNa1  = betaNa8*LCNa1+alphaNa2*CNa2+betaNa3*ONa+alphaNa5*IFNa-(betaNa2+alphaNa3+betaNa5+alphaNa8)*CNa1;
    dONa   = betaNa8*LONa+alphaNa3*CNa1+betaNa4*IFNa-(betaNa3+alphaNa4+alphaNa8)*ONa;
    dIFNa  = alphaNa4*ONa+betaNa5*CNa1+betaNa6*I1Na+alphaNa2*ICNa2-(betaNa4+alphaNa5+alphaNa6+betaNa2)*IFNa;
    dI1Na  = alphaNa6*IFNa+betaNa7*I2Na-(betaNa6+alphaNa7)*I1Na;
    dICNa2 = alphaNa1*ICNa3+betaNa2*IFNa+betaNa5*CNa2-(betaNa1+alphaNa2+alphaNa5)*ICNa2;
    dICNa3 = betaNa1*ICNa2+betaNa5*CNa3-(alphaNa1+alphaNa5)*ICNa3;
    dLONa  = alphaNa3*LCNa1+alphaNa8*ONa-(betaNa8+betaNa3)*LONa;
    dLCNa1 = alphaNa8*CNa1+alphaNa2*LCNa2+betaNa3*LONa-(betaNa8+betaNa2+alphaNa3)*LCNa1;
    dLCNa2 = betaNa2*LCNa1+alphaNa8*CNa2+alphaNa1*LCNa3-(betaNa8+betaNa1+alphaNa2)*LCNa2;
    dLCNa3 = alphaNa8*CNa3+betaNa1*LCNa2-(betaNa8+alphaNa1)*LCNa3;
    ydot(48) = dCNa2; ydot(49) = dCNa1; ydot(50) = dONa; ydot(51) = dIFNa;
    ydot(52) = dI1Na; ydot(53) = dCNa3; ydot(54) = dICNa2; ydot(55) = dICNa3;
    ydot(56) = dLONa; ydot(57) = dLCNa1; ydot(58) = dLCNa2; ydot(59) = dLCNa3;
else % If not using INa Markov, set ODEs to zero to speed simulations
    ydot(48) = 0; ydot(49) = 0; ydot(50) = 0; ydot(51) = 0; ydot(52) = 0;
    ydot(53) = 0; ydot(54) = 0; ydot(55) = 0; ydot(56) = 0; ydot(57) = 0;
    ydot(58) = 0; ydot(59) = 0;
end

I_Na_junc2 = Fjunc*GNa2*(y(50)+y(56))*(y(39)-ena_junc); % junc current
I_Na_sl2 = Fsl*GNa2*(y(50)+y(56))*(y(39)-ena_sl); % sl current
%% I_Na: compute total current (fast and late components)

if INa_MarkovFlag == 1,
    I_Na_junc = I_Na_junc2;
    I_Na_sl = I_Na_sl2;
else
    I_Na_junc = I_Na_junc1 + I_Nalj;
    I_Na_sl = I_Na_sl1 + I_Nalsl;
end

I_Na = I_Na_junc + I_Na_sl;

global I_Na_store
I_Na_store(tStep) = I_Na;
%% I_nabk: Na Background Current

I_nabk_junc = Fjunc*GNaB*(y(39)-ena_junc);
I_nabk_sl = Fsl*GNaB*(y(39)-ena_sl);
I_nabk = I_nabk_junc+I_nabk_sl;

global I_Nabk_store
I_Nabk_store(tStep) = I_nabk;
%% I_nak: Na/K Pump Current

sigma = (exp(Nao/67.3)-1)/7;
fnak = 1/(1+0.1245*exp(-0.1*y(39)*FoRT)+0.0365*sigma*exp(-y(39)*FoRT));
%KmNaip = 14; % PKA effect - 1 mM (Despa 2005)
fracPKA_PLMo = 0.116738; % Derived quantity (PLM_PKAp(baseline)/PLMtot)
fracPKA_PLMiso = 0.859251; % Derived quantity (PLM_PKAp(ISO)/PLMtot)
%kPKA_PLM=(KmNaip-14)/(fracPKA_PLMiso/fracPKA_PLMo-1); % PLM_PKAp ISO

%    PLM_PKAp = fracPKA_PLMo; % PLM clamp

kPKA_PLM=KmNaip*(1-0.7019)/(fracPKA_PLMiso/fracPKA_PLMo-1); % PLM_PKAp ISO
KmNaip_PKA=-kPKA_PLM+kPKA_PLM*(PLM_PKAp/fracPKA_PLMo);
KmNaip = KmNaip-KmNaip_PKA;
    %KmNaip = KmNaip-0.5*KmNaip_PKA; % 50% effect

I_nak_junc = Fjunc_nak*IbarNaK*fnak*Ko /(1+(KmNaip/y(32))^4) /(Ko+KmKo);
I_nak_sl = Fsl_nak*IbarNaK*fnak*Ko /(1+(KmNaip/y(33))^4) /(Ko+KmKo);
I_nak = I_nak_junc+I_nak_sl;

global I_NaK_store
I_NaK_store(tStep) = I_nak;
%% I_kur - IK,slow

xurss = 1/(1+exp(-(y(39)+15)/14));
yurss = 1/(1+exp((y(39)+48)/6.2));

tauxur = 0.95+0.05*exp(-0.08*y(39));

ydot(84) = (xurss-y(84))/tauxur;       % IKslow1
    tauxur2 = 1+7/(1+exp(-(y(39)+45)/8))+20*exp(-((y(39)+35)/10)^2);%8+20*exp(-((y(39)+35)/10)^2);
ydot(13) = (xurss-y(13))/tauxur2;      % IKslow2
%tauyur = 400+900*exp(-((y(39)+55)/16)^2)+150/(1+exp(-(y(39)+60)/8));
%ydot(85) = (yurss-y(85))/tauyur;
tauyur1 = 400+900*exp(-((y(39)+55)/16)^2)-250/(1+exp(-(y(39)+60)/8)); % fast
ydot(85) = (yurss-y(85))/tauyur1;
    tauyur2 = 400+900*exp(-((y(39)+55)/16)^2)+550/(1+exp(-(y(39)+60)/8)); % slow
    ydot(87) = (yurss-y(87))/tauyur2;

% PKA-dependent phosphoregulation of Ik,slow1 (increases Gkur1)
fracIKurp0 = 0.437635;  % Derived quantity (IKur_PKAp(baseline)/IKurtot)
fracIKurpISO = 0.718207; % Derived quantity (IKur_PKAp(ISO)/IKurtot)
%a_Kur = (1.20-1)/(fracIKurpISO/fracIKurp0-1); % +20% with 0.1 uM ISO % DEFAULT
    a_Kur = (2.00-1)/(fracIKurpISO/fracIKurp0-1); % +100%
fracIKuravail = (1-a_Kur)+a_Kur*(IKur_PKAp/fracIKurp0);

%I_kur = Kcoeff*fracIKuravail*Gkur*y(84)*y(85)*(y(39)-ek);
I_kur1 = Kcoeff*fracIKuravail*Gkur1*y(84)*y(85)*(y(39)-ek); % IKslow1
%I_kur2 = Kcoeff*fracIKuravail*Gkur2*y(84)*y(87)*(y(39)-ek); % IKslow2
I_kur2 = Kcoeff*Gkur2*y(84)*y(87)*(y(39)-ek); % IKslow2 % no PKA effect

I_kur = I_kur1 + I_kur2;

global I_kur1_store I_kur2_store
I_kur1_store(tStep) = I_kur1;
I_kur2_store(tStep) = I_kur2;
%% I_ss

xssss = xurss; % = 1/(1+exp(-(y(39)+15)/14));
%tauxss = 14+0.8*exp(-0.08*y(39));
tauxss = 70*exp(-((y(39)+43)/30)^2)+14; % Iss
ydot(86) = (xssss-y(86))/tauxss;
I_ss = Kcoeff*Gss*y(86)*(y(39)-ek); %store

global I_ss_store
I_ss_store(tStep) = I_ss;
%% I_kr: Rapidly Activating K Current

xrss = 1/(1+exp(-(y(39)+50)/7.5));
tauxr = 1/(1.38e-3*(y(39)+7)/(1-exp(-0.123*(y(39)+7)))+6.1e-4*(y(39)+10)/(exp(0.145*(y(39)+10))-1));
ydot(12) = (xrss-y(12))/tauxr;
rkr = 1/(1+exp((y(39)+33)/22.4));
I_kr = Kcoeff*gkr*y(12)*rkr*(y(39)-ek);

global I_kr_store
I_kr_store(tStep) = I_kr;
%% I_ks: Slowly Activating K Current

% Phosphoregulation of IKs by PKA parameters
% fracIKspo = 0.07344;  % Derived quantity (IKs_PKAp(baseline)/IKstot)
% fracIKsavail = (0.2*(IKs_PKAp/fracIKspo)+0.8);
% Xs05 = 1.5*(2.0 - IKs_PKAp/fracIKspo);
% 
% pcaks_junc = -log10(y(36))+3.0; 
% pcaks_sl = -log10(y(37))+3.0;  
% gks_junc = fracIKsavail*0.07*(0.057 +0.19/(1+ exp((-7.2+pcaks_junc)/0.6))); % Now regulated by PKA
% gks_sl = fracIKsavail*0.07*(0.057 +0.19/(1+ exp((-7.2+pcaks_sl)/0.6)));     % Now regulated by PKA
% eks = (1/FoRT)*log((Ko+pNaK*Nao)/(y(35)+pNaK*y(34)));	
% % xsss = 1/(1+exp(-(y(39)-1.5)/16.7)); % Original version
% xsss = 1/(1+exp(-(y(39)-Xs05)/16.7));   % Now regulated by PKA
% tauxs = 1/(7.19e-5*(y(39)+30)/(1-exp(-0.148*(y(39)+30)))+1.31e-4*(y(39)+30)/(exp(0.0687*(y(39)+30))-1)); 
%ydot(13) = 0;%(xsss-y(13))/tauxs;
    % state variable y(13) is now used for IKslow2 activation
I_ks_junc = 0;%Fjunc*gks_junc*y(13)^2*(y(39)-eks); % No IKs in mouse
I_ks_sl = 0;%Fsl*gks_sl*y(13)^2*(y(39)-eks); % No IKs in mouse
I_ks = I_ks_junc+I_ks_sl;

global IKs_store
IKs_store(tStep) = I_ks;
%% I_kp: Plateau K current

kp_kp = 1/(1+exp(7.488-y(39)/5.98));
I_kp_junc = Kcoeff*Fjunc*gkp*kp_kp*(y(39)-ek);
I_kp_sl = Kcoeff*Fsl*gkp*kp_kp*(y(39)-ek);
I_kp = I_kp_junc+I_kp_sl;
%% I_to: Transient Outward K Current (slow and fast components)

% Itos (ABSENT IN MOUSE)
xtoss = 1/(1+exp(-(y(39)+3.0)/13));
ytoss = 1/(1+exp((y(39)+48)/5));
rtoss = 1/(1+exp((y(39)+33.5)/10)); % Rto not used in MOUSE model

tauxtos = 0.08+0.7*exp(-((y(39)+25)/30)^2);
if ItoFlag == 0 % (not used)
    % Shannon Versions
    %tauytos = 3e3/(1+exp((y(39)+60.0)/10))+30;
    taurtos = 2.8e3/(1+exp((y(39)+60.0)/10))+220; % no Rto
    tauytos = 100+400/(1+exp((y(39)+25)/5));
elseif ItoFlag == 1 && CKIIflag == 0 % WT
    % Grandi Versions
    Py = 182; Pr1 = 8085; Pr2 = 313;            % Normal
    %tauytos = Py/(1+exp((y(39)+33.5)/10))+1;
    taurtos = Pr1/(1+exp((y(39)+33.5)/10))+Pr2; % no Rto
    tauytos = 100+400/(1+exp((y(39)+25)/5));
elseif ItoFlag == 1 && CKIIflag == 1            % CaMKII-OE acute effect
    Py = 15; Pr1 = 3600; Pr2 = 500;
    %GtoSlow = GtoSlow*1.5; % Rabbit
    %tauytos = Py/(1+exp((y(39)+33.5)/10))+1;
    taurtos = Pr1/(1+exp((y(39)+33.5)/10))+Pr2; % no Rto
    %tauytos = 35+400/(1+exp((y(39)+25)/5));    % MOUSE tau rec -73%
    tauytos = 100+35/(1+exp((y(39)+25)/5));     % MOUSE tau rec -73%
end

ydot(8) = (xtoss-y(8))/tauxtos;
ydot(9) = (ytoss-y(9))/tauytos;
ydot(40)= (rtoss-y(40))/taurtos;                % no Rto
%I_tos = GtoSlow*y(8)*(y(9)+0.5*y(40))*(y(39)-ek); % [uA/uF]
I_tos = 0*Kcoeff*GtoSlow*y(8)*y(9)*(y(39)-ek); % N0 Itos in MOUSE % [uA/uF]

% Itof
xtofs = 1/(1+exp(-(y(39)+3.0)/13)); % = xtoss
ytofs = 1/(1+exp((y(39)+48)/5)); % = ytoss

%tauxtof = 3.5*exp(-y(39)*y(39)/30/30)+1.5; % Original
%tauxtof = 3.5*exp(-((y(39)+3)/30)^2)+1.5; % Version in Grandi Code (does not change AP shape)
tauxtof = 0.08+0.7*exp(-((y(39)+25)/30)^2); % = tauxtos;
tauytof = 10+32*exp(-((y(39)+55)/16)^2)+8/(1+exp(-(y(39)+60)/8));
if CKIIflag == 1, % MOUSE (CaMKII-OE acute effect) % tau rec -38%
    tauytof = 5+32*exp(-((y(39)+55)/16)^2)+12/(1+exp(-(y(39)+60)/8)); 
end

ydot(10) = (xtofs-y(10))/tauxtof;
ydot(11) = (ytofs-y(11))/tauytof;
I_tof = Kcoeff*GtoFast*y(10)*y(11)*(y(39)-ek);

I_to = I_tos + I_tof;

global I_to_store
I_to_store(1,tStep) = I_to;     % Total I_to
I_to_store(2,tStep) = I_tof;    % Fast Component
I_to_store(3,tStep) = I_tos;    % Slow component
%% I_k1: Time-Independent K Current (I_ki)

aki = 1.02/(1+exp(0.2385*(y(39)-ek-59.215)));
bki =(0.49124*exp(0.08032*(y(39)+5.476-ek))+exp(0.06175*(y(39)-ek-594.31)))/(1 + exp(-0.5143*(y(39)-ek+4.753)));
kiss = aki/(aki+bki);
%I_ki = 0.9*sqrt(Ko/5.4)*kiss*(y(39)-ek); % RABBIT
if CKIIflag == 1, % MOUSE (chronic CaMKII-OE effect)
    I_ki = 1/2*0.3*sqrt(Ko/5.4)*kiss*(y(39)-ek)*Kcoeff;
else
    I_ki = 0.3*sqrt(Ko/5.4)*kiss*(y(39)-ek)*Kcoeff;
end

% % NEW!
% % PKA-dependent phosphoregulation from IKur
% fracIKurp0 = 0.437635;  % Derived quantity (IKur_PKAp(baseline)/IKurtot)
% fracIKurpISO = 0.718207; % Derived quantity (IKur_PKAp(ISO)/IKurtot)
% %a_K1 = (1.50-1)/(fracIKurpISO/fracIKurp0-1); % +50% with 0.1 uM ISO
% a_K1 = (0.50-1)/(fracIKurpISO/fracIKurp0-1); % -50% with 0.1 uM ISO
% fracIK1 = (1-a_K1)+a_K1*(IKur_PKAp/fracIKurp0); 
% 
% I_ki = I_ki*fracIK1;
% % END

global I_K1_store
I_K1_store(tStep) = I_ki;
%% I_ClCa: Ca-activated Cl Current, I_Clbk: background Cl Current

I_ClCa_junc = Fjunc*GClCa/(1+KdClCa/y(36))*(y(39)-ecl);
I_ClCa_sl = Fsl*GClCa/(1+KdClCa/y(37))*(y(39)-ecl);
I_ClCa = I_ClCa_junc+I_ClCa_sl;
I_Clbk = GClB*(y(39)-ecl);
%% Original H-H formulation for LCC - unused if ICa_MarkovFlag = 1

dss = 1/(1+exp(-(y(39)+14.5)/6.0));
taud = dss*(1-exp(-(y(39)+14.5)/6.0))/(0.035*(y(39)+14.5));
fss = 1/(1+exp((y(39)+35.06)/3.6))+0.6/(1+exp((50-y(39))/20));
tauf = 1/(0.0197*exp( -(0.0337*(y(39)+14.5))^2 )+0.02);

% ydot(4) = (dss-y(4))/taud;
% ydot(5) = (fss-y(5))/(tauf);
% ydot(6) = (1.7)*y(36)*(1-y(6))-11.9e-3*y(6); % fCa_junc  
% ydot(7) = 1.7*y(37)*(1-y(7))-11.9e-3*y(7); % fCa_sl
ydot(4) = 0;
ydot(5) = 0;
ydot(6) = 0;
ydot(7) = 0;

ibarca_j = pCa*4*(y(39)*Frdy*FoRT) * (0.341*y(36)*exp(2*y(39)*FoRT)-0.341*Cao) /(exp(2*y(39)*FoRT)-1);
ibarca_sl = pCa*4*(y(39)*Frdy*FoRT) * (0.341*y(37)*exp(2*y(39)*FoRT)-0.341*Cao) /(exp(2*y(39)*FoRT)-1);
ibark = pK*(y(39)*Frdy*FoRT)*(0.75*y(35)*exp(y(39)*FoRT)-0.75*Ko) /(exp(y(39)*FoRT)-1);
ibarna_j = pNa*(y(39)*Frdy*FoRT) *(0.75*y(32)*exp(y(39)*FoRT)-0.75*Nao)  /(exp(y(39)*FoRT)-1);
ibarna_sl = pNa*(y(39)*Frdy*FoRT) *(0.75*y(33)*exp(y(39)*FoRT)-0.75*Nao)  /(exp(y(39)*FoRT)-1);

I_Ca_junc1 = (Fjunc_CaL*ibarca_j*y(4)*y(5)*(1-y(6))*Q10CaL^Qpow)*0.45;
I_Ca_sl1 = (Fsl_CaL*ibarca_sl*y(4)*y(5)*(1-y(7))*Q10CaL^Qpow)*0.45;
I_CaK1 = (ibark*y(4)*y(5)*(Fjunc_CaL*(1-y(6))+Fsl_CaL*(1-y(7)))*Q10CaL^Qpow)*0.45;
I_CaNa_junc1 = (Fjunc_CaL*ibarna_j*y(4)*y(5)*(1-y(6))*Q10CaL^Qpow)*0.45;
I_CaNa_sl1 = (Fsl_CaL*ibarna_sl*y(4)*y(5)*(1-y(7))*Q10CaL^Qpow)*.45;
%% LCC MARKOV MODEL - based on Mahajan et al. (2008)

% This portion contains Markov state transitions for four channel types:
% 'mode 1' channels in the junction and sl and 'mode 2' channels in the
% same two compartments. Markov state transitions are computed for each
% channel type independently - total currents are the sum of the two
% channel types in each compartment (i.e. ICatot_junc = ICa_mode1_junc +
% ICa_mode2_junc). Ca-dependent transition rates differ between juncitonal
% and sl channels, whereas closing rate (r2) is adjusted to define mode1
% vs. mode2 channels. Parameters determined through microscopic
% reversibility are redefined to preserve constraint.

% CaMKII shifts distribution of junctional and subsarcolemmal channels to 
% either mode 2 at the expense of mode 1 channels (i.e. 10% mode 2 results 
% in 90% mode 1).

% PKA alters overall availability of channels (favail term that changes
% overall scaling factor for currents) and also shifts distribution of
% mode1/2 channels. PKA actions act on both junctional and sarcolemmal
% channels.

% To allow for CDI KO
cajLCC = y(36);
caslLCC = y(37);

% LCC Current Fixed Parameters
taupo = 1;          % [ms] - Time constant of activation
TBa = 450;          % [ms] - Time constant
s1o = .0221;
k1o = .03;
kop = 2.5e-3;       % [mM]
cpbar = 8e-3;       % [mM]
tca = 78.0312;
ICa_scale = 5.25;
recoveryReduc = 3;

% PKA PHOSPHOREGULATION OF LCC AVAILABLILITY (beta subunit phosph)
fracLCCbp0 = 0.250657; % Derived quantity - (LCCbp(baseline)/LCCbtot)
fracLCCbpISO = 0.525870; % Derived quantity - (LCCbp(ISO)/LCCbtot)
%a_favail=(1.50-1)/(fracLCCbpISO/fracLCCbp0-1); % fracLCCbp ISO
a_favail=(1.56-1)/(fracLCCbpISO/fracLCCbp0-1); % fracLCCbp ISO (x1.56 0.1 ISO)
%    a_favail=(2-1)/(fracLCCbpISO/fracLCCbp0-1); % fracLCCbp ISO (x1.56 0.1 ISO)
%    a_favail=(2.5-1)/(fracLCCbpISO/fracLCCbp0-1); % fracLCCbp ISO (x1.56 0.1 ISO)

favail = (1-a_favail)+a_favail*(LCCb_PKAp/fracLCCbp0); % Test (max x2.52 100% phosph)
%    favail = 1; % no PKA effect on LTCCb
ICa_scale =  ICa_scale*favail;

SSAshift=0; SSIshift=0;
% Voltage- and Ca-dependent Parameters
poss = 1/(1+exp(-(y(39)+SSAshift)/8));
fcaj = 1/(1+(kop/cajLCC)^3);            
Rv = 10 + 4954*exp(y(39)/15.6);
PrLCC = 1-1/(1+exp(-(y(39)+40)/4));     
PsLCC = 1/(1+exp(-(y(39)+40+SSIshift)/11.32));
TCaj = (tca + 0.1*(1+(cajLCC/cpbar)^2))/(1+(cajLCC/cpbar)^2); 
tauCaj = (Rv-TCaj)*PrLCC + TCaj;     
tauBa = (Rv-TBa)*PrLCC + TBa;

% Tranisition Rates (20 rates)
alphaLCC = poss/taupo;
betaLCC = (1-poss)/taupo;
r1 = 0.3;                               % [1/ms] - Opening rate
r2 = 3;                                 % [1/ms] - closing rate
s1 = s1o*fcaj; 
s1p = .00195;                           % [ms] - Inactivation rate
k1 = k1o*fcaj;  
k1p = .00413;                           % [ms] - Inactivation rate
k2 = 1e-4;                              % [ms] - Inactivation rate
k2p = .00224;                           % [ms] - Inactivation rate
s2 = s1*(k2/k1)*(r1/r2);
s2p = s1p*(k2p/k1p)*(r1/r2);
k3 = exp(-(y(39)+40)/3)/(3*(1+exp(-(y(39)+40)/3)));
k3p = k3;
k5 = (1-PsLCC)/tauCaj;
k6 = (fcaj*PsLCC)/tauCaj;
k5p = (1-PsLCC)/tauBa;

% Recovery terms
k5 = k5/recoveryReduc;
k5p = k5p/recoveryReduc;

k6p = PsLCC/tauBa;
k4 = k3*(alphaLCC/betaLCC)*(k1/k2)*(k5/k6);
k4p = k3p*(alphaLCC/betaLCC)*(k1p/k2p)*(k5p/k6p);

global gates
gates(1,tStep) = s1;
gates(2,tStep) = k1;

% State transitions for MODE 1 junctional LCCs
% O = no differential; C2 = 60; C1 = 61; I1Ca = 62; I2Ca = 63;
% I1Ba = 64; I2Ba = 65;
Po_LCCj_m1 = 1.0-y(60)-y(61)-y(62)-y(63)-y(64)-y(65);                                           % O_m1j
ydot(60) = betaLCC*y(61) + k5*y(63) + k5p*y(65) - (k6+k6p+alphaLCC)*y(60);                      % C2_m1j
ydot(61) = alphaLCC*y(60) + k2*y(62) + k2p*y(64) + r2*Po_LCCj_m1 - (r1+betaLCC+k1+k1p)*y(61);   % C1_m1j
ydot(62) = k1*y(61) + k4*y(63) + s1*Po_LCCj_m1 - (k2+k3+s2)*y(62);                              % I1Ca_m1j
ydot(63) = k3*y(62) + k6*y(60) - (k4+k5)*y(63);                                                 % I2Ca_m1j
ydot(64) = k1p*y(61) + k4p*y(65) + s1p*Po_LCCj_m1 - (k2p+k3p+s2p)*y(64);                        % I1Ba_m1j
ydot(65) = k3p*y(64) + k6p*y(60) - (k5p+k4p)*y(65);                                             % I2Ba_m1j
ibarca_jm1 = (4*pCa*y(39)*Frdy*FoRT)*(.001*exp(2*y(39)*FoRT)-0.341*Cao)/(exp(2*y(39)*FoRT)-1);
I_Ca_junc_m1 = (Fjunc_CaL*ibarca_jm1*Po_LCCj_m1*Q10CaL^Qpow)*ICa_scale;

% Re-define all parameters as mode 2 specific parameters
s1om2 = .0221;
k1om2 = .03;
kopm2 = 2.5e-3;
cpbarm2 = 8e-3;
tcam2 = 78.0312;

possm2 = 1/(1+exp(-(y(39)+SSAshift)/8));
fcajm2 = 1/(1+(kopm2/cajLCC)^3); % Depends on junctional Ca
Rvm2 = 10 + 4954*exp(y(39)/15.6);
PrLCCm2 = 1-1/(1+exp(-(y(39)+40)/4));
PsLCCm2 = 1/(1+exp(-(y(39)+40+SSIshift)/11.32));
TCajm2 = (tcam2 + 0.1*(1+(cajLCC/cpbarm2)^2))/(1+(cajLCC/cpbarm2)^2); % Caj dependent
tauCajm2 = (Rvm2-TCajm2)*PrLCCm2 + TCajm2; % Caj dependence
tauBam2 = (Rvm2-TBa)*PrLCCm2 + TBa;

alphaLCCm2 = possm2/taupo;
betaLCCm2 = (1-possm2)/taupo;
r1m2 = 0.3;                               % [1/ms] - Opening rate
r2m2 = 3/8; % [1/ms] - closing rate,  changed from rabbit (3/10) - MOUSE
s1m2 = s1om2*fcajm2; 
s1pm2 = .00195;                           % [ms] - Inactivation rate
k1m2 = k1om2*fcajm2; 
k1pm2 = .00413;                           % [ms] - Inactivation rate
k2m2 = 1e-4;                              % [ms] - Inactivation rate
k2pm2 = .00224;                           % [ms] - Inactivation rate
s2m2 = s1m2*(k2m2/k1m2)*(r1m2/r2m2);
s2pm2 = s1pm2*(k2pm2/k1pm2)*(r1m2/r2m2);
k3m2 = exp(-(y(39)+40)/3)/(3*(1+exp(-(y(39)+40)/3)));
k3pm2 = k3m2;
k5m2 = (1-PsLCCm2)/tauCajm2;
k6m2 = (fcajm2*PsLCCm2)/tauCajm2;
k5pm2 = (1-PsLCCm2)/tauBam2;
k5m2 = k5m2/recoveryReduc;      % reduced for recovery
k5pm2 = k5pm2/recoveryReduc;    % reduced for recovery    
k6pm2 = PsLCCm2/tauBam2;
k4m2 = k3m2*(alphaLCCm2/betaLCCm2)*(k1m2/k2m2)*(k5m2/k6m2);
k4pm2 = k3pm2*(alphaLCCm2/betaLCCm2)*(k1pm2/k2pm2)*(k5pm2/k6pm2);

% State transitions for MODE 2 junctional LCCs
% O = no differential; C2 = 66; C1 = 67; I1Ca = 68; I2Ca = 69;
% I1Ba = 70; I2Ba = 71;
Po_LCCj_m2 = 1.0-y(66)-y(67)-y(68)-y(69)-y(70)-y(71);                                                           % O_m2j
ydot(66) = betaLCCm2*y(67) + k5m2*y(69) + k5pm2*y(71) - (k6m2+k6pm2+alphaLCCm2)*y(66);                          % C2_m2j
ydot(67) = alphaLCCm2*y(66) + k2m2*y(68) + k2pm2*y(70) + r2m2*Po_LCCj_m2 - (r1m2+betaLCCm2+k1m2+k1pm2)*y(67);   % C1_m2j
ydot(68) = k1m2*y(67) + k4m2*y(69) + s1m2*Po_LCCj_m2 - (k2m2+k3m2+s2m2)*y(68);                                  % I1Ca_m2j
ydot(69) = k3m2*y(68) + k6m2*y(66) - (k4m2+k5m2)*y(69);                                                         % I2Ca_m2j
ydot(70) = k1pm2*y(67) + k4pm2*y(71) + s1pm2*Po_LCCj_m2 - (k2pm2+k3pm2+s2pm2)*y(70);                            % I1Ba_m2j
ydot(71) = k3pm2*y(70) + k6pm2*y(66) - (k5pm2+k4pm2)*y(71);                                                     % I2Ba_m2j
ibarca_jm2 = (4*pCa*y(39)*Frdy*FoRT)*(.001*exp(2*y(39)*FoRT)-0.341*Cao)/(exp(2*y(39)*FoRT)-1);
I_Ca_junc_m2 = (Fjunc_CaL*ibarca_jm2*(Po_LCCj_m2)*Q10CaL^Qpow)*ICa_scale;

% CaMKII AND PKA-DEPENDENT SHIFTING OF DYADIC LCCS TO MODE 2
%fpkam2 = 0.1543*LCCa_PKAp - .0043; % Assumes max phosphorylation results in 15% mode 2
fracLCCap0 = 0.219577; % Derived
frac_fpkam2 = (0.15*fracLCCap0)/(1-fracLCCap0);
fpkam2 = (0.15+frac_fpkam2)*LCCa_PKAp - frac_fpkam2; % Assumes max (100%) phosphorylation results in 15% mode 2 channels
%(fpkam2 = 0 with NO ISO)
%fpkam2 = 0; % no PKA effect on LTCCa
    %fpkam2 = 0.0765*0.8;
fckiim2 = LCC_CKp*.1; % Assumes max phosphorylation results in 10% mode 2 channels (max LCC_CKp = 1)
% Sum up total fraction of CKII and PKA-shifted mode 2 channels
junc_mode2 = fckiim2 + fpkam2;
% Total junctional ICa
I_Ca_junc2 = (1-junc_mode2)*I_Ca_junc_m1 + junc_mode2*I_Ca_junc_m2;

% SUB-SARCOLEMMAL LCCs
% Re-assign necessary params to be Casl sensitive
fcasl = 1/(1+(kop/caslLCC)^3);    % Depends on sl Ca
TCasl = (tca + 0.1*(1+(caslLCC/cpbar))^2)/(1+(caslLCC/cpbar)^2);
tauCasl = (Rv-TCasl)*PrLCC + TCasl;

% Re-assign necessary rates to be Casl sensitive
s1sl = s1o*fcasl;
k1sl = k1o*fcasl;
s2sl = s1sl*(k2/k1sl)*(r1/r2);
s2psl = s1p*(k2p/k1p)*(r1/r2);
k5sl = (1-PsLCC)/tauCasl;
k5sl = k5sl/recoveryReduc;  % Reduced for recovery
k6sl = (fcasl*PsLCC)/tauCasl;
k4sl = k3*(alphaLCC/betaLCC)*(k1sl/k2)*(k5sl/k6sl);
k4psl = k3p*(alphaLCC/betaLCC)*(k1p/k2p)*(k5p/k6p);

% State transitions for 'mode 1' sarcolemmal LCCs
% O = no differential; C2 = 72; C1 = 73; I1Ca = 74; I2Ca = 75;
% I1Ba = 76; I2Ba = 77;
Po_LCCsl_m1 = 1-y(72)-y(73)-y(74)-y(75)-y(76)-y(77);                                                % O_m1sl
ydot(72) = betaLCC*y(73) + k5sl*y(75) + k5p*y(77) - (k6sl+k6p+alphaLCC)*y(72);                      % C2_m1sl
ydot(73) = alphaLCC*y(72) + k2*y(74) + k2p*y(76) + r2*Po_LCCsl_m1 - (r1+betaLCC+k1sl+k1p)*y(73);    % C1_m1sl
ydot(74) = k1sl*y(73) + k4sl*y(75) + s1sl*Po_LCCsl_m1 - (k2+k3+s2sl)*y(74);                         % I1Ca_m1sl
ydot(75) = k3*y(74) + k6sl*y(72) - (k4sl+k5sl)*y(75);                                               % I2Ca_m1sl
ydot(76) = k1p*y(73) + k4psl*y(77) + s1p*Po_LCCsl_m1 - (k2p+k3p+s2psl)*y(76);                       % I1Ba_m1sl
ydot(77) = k3p*y(76) + k6p*y(72) - (k5p+k4psl)*y(77);                                               % I2Ba_m1sl
ibarca_slm1 = (4*pCa*y(39)*Frdy*FoRT)*(.001*exp(2*y(39)*FoRT)-0.341*Cao)/(exp(2*y(39)*FoRT)-1);
I_Casl_m1 = (Fsl_CaL*ibarca_slm1*Po_LCCsl_m1*Q10CaL^Qpow)*ICa_scale;

% Adjust closing rate for 'mode 2' sarcolemmal LCCs
r2slm2 = r2m2;
s2slm2 = s1sl*(k2/k1sl)*(r1/r2slm2);
s2pslm2 = s1p*(k2p/k1p)*(r1/r2slm2);

% State transitions for mode 2 sarcolemmal LCCs
% O = no differential; C2 = 78; C1 = 79; I1Ca = 80; I2Ca = 81; I1Ba = 82; I2Ba = 83
Po_LCCsl_m2 = 1-y(78)-y(79)-y(80)-y(81)-y(82)-y(83);                                                % O_m2sl
ydot(78) = betaLCC*y(79) + k5sl*y(81) + k5p*y(83) - (k6sl+k6p+alphaLCC)*y(78);                      % C2_m2sl
ydot(79) = alphaLCC*y(78) + k2*y(80) + k2p*y(82) + r2slm2*Po_LCCsl_m2 - (r1+betaLCC+k1sl+k1p)*y(79);% C1_m2sl
ydot(80) = k1sl*y(79) + k4sl*y(81) + s1sl*Po_LCCsl_m2 - (k2+k3+s2slm2)*y(80);                       % I1Ca_m2sl
ydot(81) = k3*y(80) + k6sl*y(78) - (k4sl+k5sl)*y(81);                                               % I2Ca_m2sl
ydot(82) = k1p*y(79) + k4psl*y(83) + s1p*Po_LCCsl_m2 - (k2p+k3p+s2pslm2)*y(82);                     % I1Ba_m2sl
ydot(83) = k3p*y(82) + k6p*y(78) - (k5p+k4psl)*y(83);                                               % I2Ba_m2sl
ibarca_slm2 = (4*pCa*y(39)*Frdy*FoRT)*(.001*exp(2*y(39)*FoRT)-0.341*Cao)/(exp(2*y(39)*FoRT)-1);
I_Casl_m2 = (Fsl_CaL*ibarca_slm2*Po_LCCsl_m2*Q10CaL^Qpow)*ICa_scale;

% Sum mode 1 and mode 2 sl channels for total sl current
fckiim2_sl = 0; % Set to zero since SL LCCp by CaMKII is negligible
sl_mode2 = fckiim2_sl + fpkam2;
I_Ca_sl2 = (1-sl_mode2)*I_Casl_m1 + sl_mode2*I_Casl_m2; 

% Na and K currents through LCC
I_CaKj2 = ibark*Fjunc_CaL*((1-junc_mode2)*Po_LCCj_m1 + junc_mode2*Po_LCCj_m2)*Q10CaL^Qpow*ICa_scale; 
I_CaKsl2 = ibark*Fsl_CaL*((1-sl_mode2)*Po_LCCsl_m1 + sl_mode2*Po_LCCsl_m2)*Q10CaL^Qpow*ICa_scale;
I_CaK2 = I_CaKj2+I_CaKsl2;
I_CaNa_junc2 = (Fjunc_CaL*ibarna_j*((1-junc_mode2)*Po_LCCj_m1+junc_mode2*Po_LCCj_m2)*Q10CaL^Qpow)*ICa_scale;
I_CaNa_sl2 = Fsl_CaL*ibarna_sl*((1-sl_mode2)*Po_LCCsl_m1 + sl_mode2*Po_LCCsl_m2)*Q10CaL^Qpow*ICa_scale;

% These are now able to switch depending on whether or not the flag to
% switch to Markov model of ICa is ON
I_Ca_junc = (1-ICa_MarkovFlag)*I_Ca_junc1 + ICa_MarkovFlag*I_Ca_junc2;
I_Ca_sl = (1-ICa_MarkovFlag)*I_Ca_sl1 + ICa_MarkovFlag*I_Ca_sl2;
I_Ca = I_Ca_junc+I_Ca_sl;   % Total Ca curren throuhgh LCC
I_CaNa_junc = (1-ICa_MarkovFlag)*(I_CaNa_junc1) + (ICa_MarkovFlag)*(I_CaNa_junc2);
I_CaNa_sl = (1-ICa_MarkovFlag)*(I_CaNa_sl1) + (ICa_MarkovFlag)*(I_CaNa_sl2);
I_CaNa = I_CaNa_junc + I_CaNa_sl;   % Total Na current through LCC
I_CaK = (1-ICa_MarkovFlag)*(I_CaK1) + ICa_MarkovFlag*(I_CaK2);  % Total K current through LCC

% Collect all currents through LCC
I_Catot = I_Ca+I_CaK+I_CaNa;
ydot(43)=-I_Ca*Cmem/(Vmyo*2*Frdy)*1e3;

global I_Ca_store ibar_store
I_Ca_store(tStep) = I_Catot;
ibar_store(tStep) = ibarca_j;
%% I_ncx: Na/Ca Exchanger flux

Ka_junc = 1/(1+(Kdact/y(36))^3);
Ka_sl = 1/(1+(Kdact/y(37))^3);
s1_junc = exp(nu*y(39)*FoRT)*y(32)^3*Cao;
s1_sl = exp(nu*y(39)*FoRT)*y(33)^3*Cao;
s2_junc = exp((nu-1)*y(39)*FoRT)*Nao^3*y(36);
s3_junc = (KmCai*Nao^3*(1+(y(32)/KmNai)^3)+KmNao^3*y(36)+ KmNai^3*Cao*(1+y(36)/KmCai)+KmCao*y(32)^3+y(32)^3*Cao+Nao^3*y(36))*(1+ksat*exp((nu-1)*y(39)*FoRT));
s2_sl = exp((nu-1)*y(39)*FoRT)*Nao^3*y(37);
s3_sl = (KmCai*Nao^3*(1+(y(33)/KmNai)^3) + KmNao^3*y(37)+KmNai^3*Cao*(1+y(37)/KmCai)+KmCao*y(33)^3+y(33)^3*Cao+Nao^3*y(37))*(1+ksat*exp((nu-1)*y(39)*FoRT));
I_ncx_junc = Fjunc_ncx*IbarNCX*Q10NCX^Qpow*Ka_junc*(s1_junc-s2_junc)/s3_junc;
I_ncx_sl = Fsl_ncx*IbarNCX*Q10NCX^Qpow*Ka_sl*(s1_sl-s2_sl)/s3_sl;
I_ncx = I_ncx_junc+I_ncx_sl;
ydot(45)=2*I_ncx*Cmem/(Vmyo*2*Frdy)*1e3; %uM/ms

global Incx
Incx(tStep) = I_ncx;
%% I_pca: Sarcolemmal Ca Pump Current

I_pca_junc = Fjunc*Q10SLCaP^Qpow*IbarSLCaP*y(36)^1.6/(KmPCa^1.6+y(36)^1.6);
I_pca_sl = Fsl*Q10SLCaP^Qpow*IbarSLCaP*y(37)^1.6/(KmPCa^1.6+y(37)^1.6);
I_pca = I_pca_junc+I_pca_sl;
ydot(44)=-I_pca*Cmem/(Vmyo*2*Frdy)*1e3;

global Ipca_store
Ipca_store(tStep) = I_pca;
%% I_cabk: Ca Background Current

I_cabk_junc = Fjunc*GCaB*(y(39)-eca_junc);
I_cabk_sl = Fsl*GCaB*(y(39)-eca_sl);
I_cabk = I_cabk_junc+I_cabk_sl;
ydot(46)=-I_cabk*Cmem/(Vmyo*2*Frdy)*1e3;
%% I_CFTR or I_cl_(cAMP) - Cystic Fibrosis Transmembrane Conductance Reg.
% This is an Em- and time-independent current that is activated by PKA
% fact_pka_cftr = 1.1933*ICFTR_PKAp - 0.1933; % Derived?
% gCFTR = fact_pka_cftr*4.9e-3; % [A/F] - Max value as in Shannon et al. (2005)
Icftr = 0; %gCFTR*(y(39) - ecl); % NO Icftr in MOUSE

global ICFTR
ICFTR(tStep) = Icftr;
%% RyR model - SR release fluxes and leak

% CaMKII and PKA-dependent phosphoregulation of RyR Po
fCKII_ec50SR = 1.16 - 4/5*RyR_CKp;
ec50SR = fCKII_ec50SR*ec50SR; % MOUSE - 60% 

MaxSR = 15; MinSR = 1;
kCaSR = MaxSR - (MaxSR-MinSR)/(1+(ec50SR/y(31))^2.5);
koSRCa = koCa/kCaSR;
kiSRCa = kiCa*kCaSR;
kleak = 2*5.348e-6; % [1/ms] changed from rabbit (5.348e-6)

%fCKII_RyR = (20*RyR_CKp/3 - 1/3); % 1 at basal condition - RABBIT
fCKII_RyR = (10*RyR_CKp - 1); % 1 at basal condition - MOUSE

%fPKA_RyR = RyR_PKAp*1.025 + 0.9750; % 1 with NO ISO
frac_RyRo = 0.204276; % Derived (RyR_PKAp(basal)/RyRtot)
    %RyR_PKAp = frac_RyRo;
a_RyR = (2-1)/(1/frac_RyRo-1); % Max effect: fPKA_RyR=2
fPKA_RyR = 1-a_RyR+a_RyR*(RyR_PKAp/frac_RyRo);
koSRCa = (fCKII_RyR + fPKA_RyR - 1)*koSRCa;

% ODEs for RyR states and SR release through open RyRs
RI = 1-y(14)-y(15)-y(16);
ydot(14) = (kim*RI-kiSRCa*y(36)*y(14))-(koSRCa*y(36)^2*y(14)-kom*y(15));   % R
ydot(15) = (koSRCa*y(36)^2*y(14)-kom*y(15))-(kiSRCa*y(36)*y(15)-kim*y(16));% O
ydot(16) = (kiSRCa*y(36)*y(15)-kim*y(16))-(kom*y(16)-koSRCa*y(36)^2*RI);   % I
J_SRCarel = ks*y(15)*(y(31)-y(36));          % [mmol/L SR/ ms]

% Passive RyR leak - includes CaMKII regulation of leak flux
%kleak = (1/3 + 10*RyR_CKp/3)*kleak; % RABBIT
kleak = (1/2 + 5*RyR_CKp/2)*kleak; % MOUSE (reduced CaMKII effect on leak)
J_SRleak = kleak*(y(31)-y(36)); % [mmol/L cyt/ms]

global Jleak 
Jleak(tStep,1) = J_SRCarel*Vsr/Vmyo + J_SRleak; % Total leak [mmol/L cyt/ms]
Jleak(tStep,2) = J_SRleak;                      % Passive leak only [mmol/L cyt/ms]  
%% SERCA model - SR uptake fluxes

% CaMKII and PKA-dependent phosphoregulation of PLB (changes to SERCA flux)
fCKII_PLB = (1-.5*PLB_CKp); % Max effect: fCKII_PLB=0.5
fracPKA_PLBo = 1-0.079755; % Derived quantity - (1 - (PLBp(baseline)/PLBtot))
fPKA_PLB = (PLB_PKAn/fracPKA_PLBo)*3/4 + 1/4; % Max effect: fPKA_PLB=0.25
%    PLB_PKAn = fracPKA_PLBo;
fPKA_PLB = (PLB_PKAn/fracPKA_PLBo)*(100-55.31)/100 + 55.31/100; % Max effect: fPKA_PLB=0.45

% Select smaller value (resulting in max reduction of Kmf)
if fCKII_PLB < fPKA_PLB
    Kmf = Kmf*fCKII_PLB;%fCKII_PLB
elseif fPKA_PLB < fCKII_PLB
    Kmf = Kmf*fPKA_PLB;%fPKA_PLB
end

J_serca = Q10SRCaP^Qpow*Vmax_SRCaP*((y(38)/Kmf)^hillSRCaP-(y(31)/Kmr)^hillSRCaP)...
    /(1+(y(38)/Kmf)^hillSRCaP+(y(31)/Kmr)^hillSRCaP); % [mM/msec] 

global Jserca
Jserca(tStep) = J_serca; % [mM/msec] or [mmol/L cyt msec]
%% Na and Ca Buffering

ydot(17) = kon_na*y(32)*(Bmax_Naj-y(17))-koff_na*y(17);        % NaBj      [mM/ms]
ydot(18) = kon_na*y(33)*(Bmax_Nasl-y(18))-koff_na*y(18);       % NaBsl     [mM/ms]

% Cytosolic Ca Buffers
ydot(19) = kon_tncl*y(38)*(Bmax_TnClow-y(19))-koff_tncl*y(19);            % TnCL      [mM/ms]
ydot(20) = kon_tnchca*y(38)*(Bmax_TnChigh-y(20)-y(21))-koff_tnchca*y(20); % TnCHc     [mM/ms]
ydot(21) = kon_tnchmg*Mgi*(Bmax_TnChigh-y(20)-y(21))-koff_tnchmg*y(21);   % TnCHm     [mM/ms]
ydot(22) = 0; % commented b/c buffering done by CaM module
% kon_cam*y(38)*(Bmax_CaM-y(22))-koff_cam*y(22); % CaM       [mM/ms]
ydot(23) = kon_myoca*y(38)*(Bmax_myosin-y(23)-y(24))-koff_myoca*y(23);    % Myosin_ca [mM/ms]
ydot(24) = kon_myomg*Mgi*(Bmax_myosin-y(23)-y(24))-koff_myomg*y(24);      % Myosin_mg [mM/ms]
ydot(25) = kon_sr*y(38)*(Bmax_SR-y(25))-koff_sr*y(25);                    % SRB       [mM/ms]
%J_CaB_cytosol = sum(ydot(19:25)); % wrong formulation
J_CaB_cytosol = ydot(19)+ydot(20)+ydot(22)+ydot(23)+ydot(25);

% Junctional and SL Ca Buffers
ydot(26) = kon_sll*y(36)*(Bmax_SLlowj-y(26))-koff_sll*y(26);       % SLLj      [mM/ms]
ydot(27) = kon_sll*y(37)*(Bmax_SLlowsl-y(27))-koff_sll*y(27);      % SLLsl     [mM/ms]
ydot(28) = kon_slh*y(36)*(Bmax_SLhighj-y(28))-koff_slh*y(28);      % SLHj      [mM/ms]
ydot(29) = kon_slh*y(37)*(Bmax_SLhighsl-y(29))-koff_slh*y(29);     % SLHsl     [mM/ms]
J_CaB_junction = ydot(26)+ydot(28);
J_CaB_sl = ydot(27)+ydot(29);
%% Ion concentrations

% SR Ca Concentrations
ydot(30) = kon_csqn*y(31)*(Bmax_Csqn-y(30))-koff_csqn*y(30); % Csqn      [mM/ms]
ydot(31) = J_serca*Vmyo/Vsr-(J_SRleak*Vmyo/Vsr+J_SRCarel)-ydot(30); % Ca_sr     [mM/ms] % Ratio 3 leak current

% Na Concentrations
I_Na_tot_junc = I_Na_junc+I_nabk_junc+3*I_ncx_junc+3*I_nak_junc+I_CaNa_junc;   % [uA/uF]
I_Na_tot_sl = I_Na_sl+I_nabk_sl+3*I_ncx_sl+3*I_nak_sl+I_CaNa_sl;   %[uA/uF]
ydot(32) = -I_Na_tot_junc*Cmem/(Vjunc*Frdy)+J_na_juncsl/Vjunc*(y(33)-y(32))-ydot(17);
ydot(33) = -I_Na_tot_sl*Cmem/(Vsl*Frdy)+J_na_juncsl/Vsl*(y(32)-y(33))...
  +J_na_slmyo/Vsl*(y(34)-y(33))-ydot(18);
if NaClampFlag == 1,
    ydot(34) = 0; % Na clamp
else
    ydot(34) = J_na_slmyo/Vmyo*(y(33)-y(34)); % [mM/msec]
end

% K Concentration
I_K_tot = I_to+I_kr+I_ks+I_ki-2*I_nak+I_CaK+I_kp+I_kur+I_ss;     % [uA/uF]
ydot(35) = 0; %-I_K_tot*Cmem/(Vmyo*Frdy);           % [mM/msec]

% Ca Concentrations
I_Ca_tot_junc = I_Ca_junc+I_cabk_junc+I_pca_junc-2*I_ncx_junc; % [uA/uF]
I_Ca_tot_sl = I_Ca_sl+I_cabk_sl+I_pca_sl-2*I_ncx_sl;           % [uA/uF]
ydot(36) = -I_Ca_tot_junc*Cmem/(Vjunc*2*Frdy)+J_ca_juncsl/Vjunc*(y(37)-y(36))...
  -J_CaB_junction+(J_SRCarel)*Vsr/Vjunc+J_SRleak*Vmyo/Vjunc;   % Ca_j
ydot(37) = -I_Ca_tot_sl*Cmem/(Vsl*2*Frdy)+J_ca_juncsl/Vsl*(y(36)-y(37))...
  + J_ca_slmyo/Vsl*(y(38)-y(37))-J_CaB_sl;   % Ca_sl
ydot(38) = -J_serca-J_CaB_cytosol +J_ca_slmyo/Vmyo*(y(37)-y(38)); % Cai
junc_sl=J_ca_juncsl/Vsl*(y(36)-y(37));
sl_junc=J_ca_juncsl/Vjunc*(y(37)-y(36));
sl_myo=J_ca_slmyo/Vsl*(y(38)-y(37));
myo_sl=J_ca_slmyo/Vmyo*(y(37)-y(38));
%% Simulation type

if CaffeineFlag==1,
    protocol = 'vcRest';
end
if StrophFlag==1,
    protocol = 'none';
end

% AP Waveform for AP clamp & HR control
global AP % APc_t APc_Vm
global stim stim_t stim_t0 stim_period stim_apd

switch protocol
    case {'none',''},
        I_app = 0;
    case 'pace',    % pace w/ current injection at cycleLength 'cycleLength'
        if mod(t,cycleLength) <= 5
            I_app = 9.5;
        else
            I_app = 0.0;
        end
    case 'pace_hr_control',    
        ind = find(stim_t>=t);
        I_app = 9.5 * stim(ind(1));
    case 'vcRest'   % Resting vclamp to equilibrate cell at resting potential
        V_clamp = -83;%y(39);%-80;
        R_clamp = .01;
        I_app = (V_clamp-y(39))/R_clamp;
    case 'vclamp_ICa', % Based on Kohlhaas (2006), Maier (2003)  
		V_hold = -90;
        V_test = 20; % Use 0.05 for 0 mV to avoid numerical problems
        V_step = -50;
        INa_inactT = 30; % ms
		if mod(t,cycleLength) <= INa_inactT
		    V_clamp = V_step;
        elseif mod(t,cycleLength)>INa_inactT && mod(t,cycleLength)<= 200 + INa_inactT
		    V_clamp = V_test;
        else
            V_clamp = V_hold;
		end
		R_clamp = 0.01;
		I_app = (V_clamp-y(39))/R_clamp;
    case 'vclamp_ICa_Gain'
        V_hold = -80;
        V_test = 20;%0.05;
%         if t>1e3
%             V_test = -10;
%         end
        if mod(t,cycleLength)>= 5 &&  mod(t,cycleLength) <= 35%205
            V_clamp = V_test;
        else
            V_clamp = V_hold;
        end
        R_clamp = 0.01;
		I_app = (V_clamp-y(39))/R_clamp;
    case 'I-V_ICa'
        % Start with 5 pre-pulses at 0.5 Hz (200 ms each) from -90 to 0 mV
        V_hold = -90;
        V_condition = 0;
        V_step = -50;
        V_test = -30;
        if t < 10e3
            if mod(t,cycleLength) <= 200
                V_clamp = V_condition;
            else 
                V_clamp = V_hold;
            end
        else
            if mod(t,cycleLength) <= 50
                V_clamp = V_step;
            elseif mod(t,cycleLength) > 50 && mod(t,cycleLength) <= 250
                V_clamp = V_test;
            else
                V_clamp = V_hold;
            end
        end
        R_clamp = 0.01;
		I_app = (V_clamp-y(39))/R_clamp;  
    case 'IV_SSI_ICa'
        V_hold1 = -90;
        V_condition = variablePar;
        V_hold2 = V_hold1;
        V_step = 0.05;
        if mod(t,cycleLength) <= 250
            V_clamp = V_hold1;
        elseif mod(t,cycleLength) > 250 && mod(t,cycleLength) <= 2250
            V_clamp = V_condition;
        elseif mod(t,cycleLength) > 2250 && mod(t,cycleLength) <= 2255
            V_clamp = V_hold2;
        elseif mod(t,cycleLength) > 2255 && mod(t,cycleLength) <= 2455
            V_clamp = V_step;
        else
            V_clamp = V_hold1;
        end
        R_clamp = 0.01;
		I_app = (V_clamp-y(39))/R_clamp;    
    case 'recovery_ICa' % Based on protocol from Li 1997 in ferret
        V_hold1 = -70;
        V_hold2 = -90;
        V_hold3 = -90; % Vary this term to change holding potential of experiment
        V_test = 0;
        if t <= 10e3
            if mod(t,cycleLength) <= 200
                V_clamp = V_test;
            else
                V_clamp = V_hold1;
            end
        elseif t>10e3 && t<= 12e3 % 2 s at -90 mV
            V_clamp = V_hold2;
        elseif t>12e3 && t<= 12.5e3 % First 500 ms pulse
            V_clamp = V_test;
        elseif t > 12.5e3 && t <= 12.5e3+rest % Variable rest interval
            V_clamp = V_hold3;
        elseif t > 12.5e3+rest && t <= 12.5e3+rest+500 % Second, 500 ms test pulse
            V_clamp = V_test;
        else
            V_clamp = V_hold2;
        end
        R_clamp = 0.01;
		I_app = (V_clamp-y(39))/R_clamp;        
    case 'recovery_Ito'
        V_hold = -80;
        V_test = +50;
        if t <= 500
            V_clamp = V_test;
        elseif t > 500 && t <= 500 + rest
            V_clamp = V_hold;
        elseif t > 500 + rest && t <= 1e3 + rest
            V_clamp = V_test;
        else 
            V_clamp = V_hold;
        end
        R_clamp = .01;
        I_app = (V_clamp-y(39))/R_clamp;
    case 'vclamp_INa'
        V_hold = -140;
        V_test = -20;
        if mod(t,cycleLength) <= 500
            V_clamp = V_test;
        else
            V_clamp = V_hold;
        end
        R_clamp = .01;
        I_app = (V_clamp-y(39))/R_clamp;
    case 'recovery_INa'
        V_hold = -140;
        V_test = -20;
        if t <= 1e3
            V_clamp = V_test;
        elseif t > 1e3 && t <= 1e3 + rest
            V_clamp = V_hold;
        elseif t > 1e3 + rest && t <= 1e3 + rest + 10
            V_clamp = V_test;
        else 
            V_clamp = V_hold;
        end
        R_clamp = .01;
        I_app = (V_clamp-y(39))/R_clamp;
    case 'step', % SM
		V_hold = -90;
        V_test = 0.05; % Use 0.05 for 0 mV to avoid numerical problems
        V_step = -90;
        INa_inactT = 20; % delay (ms)
		if mod(t,cycleLength) <= INa_inactT
		    V_clamp = V_step;
        elseif mod(t,cycleLength)>INa_inactT && mod(t,cycleLength)<= 200 + INa_inactT
		    V_clamp = V_test;
        else
            V_clamp = V_hold;
		end
		R_clamp = 0.01;
		I_app = (V_clamp-y(39))/R_clamp;
    case 'AP_clamp'
        % Determine appropriate voltage by interpolating between data points
        % Note - use mod(t,1e3) for 1 Hz data
        %AP_clamp_period = 1e3; % 1 Hz
        AP_clamp_freq = 5; % Hz
        AP_clamp_period = 1e3/AP_clamp_freq; % ms
        ind1 = find(AP(:,1) <= mod(t,AP_clamp_period),1,'last');
        ind2 = find(AP(:,1) >= mod(t,AP_clamp_period),1,'first');
        tint = [AP(ind1,1),mod(t,AP_clamp_period),AP(ind2,1)];
        APint = interp1(AP(:,1),AP(:,2),tint);
        potential = APint(2);
        
        R_clamp = .01;
        I_app = (potential-y(39))/R_clamp;
	case 'AP_clamp_hr_control'
        % AP clamp at different pacing frequency (& APD moduation)
        ind = find(stim_t>=t);
        AP_clamp_t0 = stim_t0(ind(1)); % stim_t0
        AP_clamp_period = stim_period(ind(1)); % stim_period
        %AP_t = AP(:,1)*1;
            AP_t(:,1) = AP(:,1)*stim_apd(ind(1)); % APD modulation
        AP_v = AP(:,2);
        ind1 = find(AP_t <= mod(t-AP_clamp_t0,AP_clamp_period),1,'last');
        ind2 = find(AP_t >= mod(t-AP_clamp_t0,AP_clamp_period),1,'first');
        tint = [AP_t(ind1),mod(t-AP_clamp_t0,AP_clamp_period),AP_t(ind2)];
        APint = interp1(AP_t,AP_v,tint);
        potential = APint(2);
        
        R_clamp = .01;
        I_app = (potential-y(39))/R_clamp;
	case 'AP_clamp_hr_control_UP'
        % AP clamp at different pacing frequency (& APD moduation)
        % and unchanged upstroke!
        ind = find(stim_t>=t);
        AP_clamp_t0 = stim_t0(ind(1)); % stim_t0
        AP_clamp_period = stim_period(ind(1)); % stim_period
        
        [up ind_up]=max(AP(:,2));
        %t_peak = 0.621*AP(ind_up,1);
            
            AP_t = AP(:,1);
            AP_t(1:ind_up) = 0.621*AP(1:ind_up,1);
            AP_t(ind_up+1:end) = 0.621*AP_t(ind_up+1)+(AP_t(ind_up+1:end)-AP_t(ind_up+1))*stim_apd(ind(1)); % APD modulation
            AP_v = AP(:,2);

        ind1 = find(AP_t <= mod(t-AP_clamp_t0,AP_clamp_period),1,'last');
        ind2 = find(AP_t >= mod(t-AP_clamp_t0,AP_clamp_period),1,'first');
        tint = [AP_t(ind1),mod(t-AP_clamp_t0,AP_clamp_period),AP_t(ind2)];
        APint = interp1(AP_t,AP_v,tint);
        potential = APint(2);
                
        R_clamp = .01;
        I_app = (potential-y(39))/R_clamp;
end  
%% Membrane Potential

I_Na_tot = I_Na_tot_junc + I_Na_tot_sl;                 % [uA/uF]
I_Cl_tot = I_ClCa+I_Clbk+Icftr;                         % [uA/uF]
I_Ca_tot = I_Ca_tot_junc+I_Ca_tot_sl;                   % [uA/uF]
I_tot = I_Na_tot+I_Cl_tot+I_Ca_tot+I_K_tot;             % [uA/uF]
ydot(39) = -(I_tot-I_app);

global dVm_store 
dVm_store(tStep) = ydot(39);