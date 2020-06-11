% Main file: morotti_et_al_mouse_masterCompute
%
% Please cite the following paper when using this model:
% Morotti S, Edwards AG, McCulloch AD, Bers DM & Grandi E. (2014). A novel
% computational model of mouse myocyte electrophysiology to assess the
% synergy between Na(+) loading and CaMKII. Journal of Physiology, doi:
% 10.1113/jphysiol.2013.266676.
%
% This model was built upon the code of the Soltis and Saucerman model
% of rabbit ventricular EC coupling.
% Reference: Soltis AR & Saucerman JJ. (2010). Synergy between CaMKII
% substrates and beta-adrenergic signaling in regulation of cardiac
% myocyte Ca(2+) handling. Biophysical Journal 99, 2038-2047.
%
% This file loads initial conditions, calls the ode solver and plots
% simulation results.

%%
function main(AP_datafile, initcond_datafile, APDMode, StimProtocol)

% disp('Mouse model - Morotti et al.')
%% Parameters for external modules
% ECC and CaM modules
freq = 1;                   % [Hz] - CHANGE DEPENDING ON FREQUENCY
cycleLength = 1e3/freq;     % [ms]
CaMtotDyad = 418;           % [uM]
BtotDyad = 1.54/8.293e-4;   % [uM]
CaMKIItotDyad = 120;        % [uM]
CaNtotDyad = 3e-3/8.293e-4; % [uM]
PP1totDyad = 96.5;          % [uM]
CaMtotSL = 5.65;            % [uM]
BtotSL = 24.2;              % [uM]
CaMKIItotSL = 120*8.293e-4; % [uM]
CaNtotSL = 3e-3;            % [uM]
PP1totSL = 0.57;            % [uM]
CaMtotCyt = 5.65;           % [uM]
BtotCyt = 24.2;             % [uM]
CaMKIItotCyt = 120*8.293e-4;% [uM]
CaNtotCyt = 3e-3;           % [uM]
PP1totCyt = 0.57;           % [uM]

% ADJUST CaMKII ACTIVITY LEVELS (expression = 'WT', 'OE', or 'KO')
expression = 'WT';

CKIIOE = 0; % Should be zero during 'WT' and 'KO' runs
if strcmp(expression,'OE') % OE
    CKIIOE = 1; % Flag for CaMKKII-OE (0=WT, 1=OE)
    n_OE=6;
    CaMKIItotDyad = 120*n_OE;         % [uM]
    CaMKIItotSL = 120*8.293e-4*n_OE;  % [uM]
    CaMKIItotCyt = 120*8.293e-4*n_OE; % [uM]
elseif strcmp(expression,'KO')
    CaMKIItotDyad = 0;          % [uM]
    CaMKIItotSL = 0;            % [uM]
    CaMKIItotCyt = 0;           % [uM]
end

%plb_val=38; % RABBIT
plb_val=106; % MOUSE

% Parameters for CaMKII module
LCCtotDyad = 31.4*.9;       % [uM] - Total Dyadic [LCC] - (umol/l dyad)
LCCtotSL = 0.0846;          % [uM] - Total Subsarcolemmal [LCC] (umol/l sl)
RyRtot = 382.6;             % [uM] - Total RyR (in Dyad)
PP1_dyad = 95.7;            % [uM] - Total dyadic [PP1]
PP1_SL = 0.57;              % [uM] - Total Subsarcolemmal [PP1]
PP2A_dyad = 95.76;          % [uM] - Total dyadic PP2A
OA = 0;                     % [uM] - PP1/PP2A inhibitor Okadaic Acid
PLBtot = plb_val;           % [uM] - Total [PLB] in cytosolic units

% Parameters for BAR module
Ligtot = 0;% 0.100          % [uM] - SET LIGAND CONCENTRATION (0 or 0.1)
LCCtotBA = 0.025;           % [uM] - [umol/L cytosol]
RyRtotBA = 0.135;           % [uM] - [umol/L cytosol]
PLBtotBA = plb_val;         % [uM] - [umol/L cytosol]
TnItotBA = 70;              % [uM] - [umol/L cytosol]
IKstotBA = 0.025;           % [uM] - [umol/L cytosol]
ICFTRtotBA = 0.025;         % [uM] - [umol/L cytosol]
PP1_PLBtot = 0.89;          % [uM] - [umol/L cytosol]
IKurtotBA = 0.025;          % [uM] - [umol/L cytosol] MOUSE
PLMtotBA = 48;              % [uM] - [umol/L cytosol] MOUSE

% For Recovery from inactivation of LTCC
recoveryTime = 10; % initialize to smallest value

% Parameter varied in protocol simulation
variablePar = 20; % initialization
%% Collect all parameters and define mass matrix for BAR module

%global p
p = [cycleLength,recoveryTime,variablePar,CaMtotDyad,BtotDyad,CaMKIItotDyad,...
    CaNtotDyad,PP1totDyad,CaMtotSL,BtotSL,CaMKIItotSL,CaNtotSL,PP1totSL,...
    CaMtotCyt,BtotCyt,CaMKIItotCyt,CaNtotCyt,PP1totCyt,...
    LCCtotDyad,RyRtot,PP1_dyad,PP2A_dyad,OA,PLBtot,LCCtotSL,PP1_SL,...
    Ligtot,LCCtotBA,RyRtotBA,PLBtotBA,TnItotBA,IKstotBA,ICFTRtotBA,...
    PP1_PLBtot,IKurtotBA,PLMtotBA,CKIIOE];
%% Establish and define global variables

global AP
load(AP_datafile); % Experimental AP signal
% load exp_APc_data_5Hz % Experimental AP signal
APc_t = [APc_t;10000];
APc_Vm = [APc_Vm;APc_Vm(1)];
AP = [APc_t APc_Vm];

%[val_max ind_max] = max(APc_Vm)
%t_peak = 0.621*APc_t(ind_max)

global tStep tArray I_Ca_store I_to_store I_Na_store I_K1_store ibar_store
global gates Jserca IKs_store Jleak ICFTR Incx
global I_ss_store dVm_store Ipca_store I_NaK_store I_Nabk_store I_kr_store
global I_kur1_store I_kur2_store

tStep = 1;
tArray = zeros(1,1e6);
I_Ca_store = zeros(1,1e6);
I_to_store = zeros(3,1e6);
I_Na_store = zeros(1,1e6);
I_K1_store = zeros(1,1e6);
ibar_store = zeros(1,1e6);
gates = zeros(2,1e6);
Jserca = zeros(1,1e6);
IKs_store = zeros(1,1e6);
Jleak = zeros(1e6,2);
ICFTR = zeros(1,1e6);
Incx = zeros(1,1e6);
I_kur1_store = zeros(1,1e6);
I_kur2_store = zeros(1,1e6);
I_ss_store = zeros(1,1e6);
dVm_store = zeros(1,1e6);
Ipca_store = zeros(1,1e6);
I_NaK_store = zeros(1,1e6);
I_Nabk_store = zeros(1,1e6);
I_kr_store = zeros(1,1e6);
%% HR control

global stim stim_t stim_t0 stim_period stim_apd

sim_duration = 10e3; % ms
stim_t = (0:0.1:sim_duration); % ms

HR_modulation = 1;
if HR_modulation == 0,
    % constant
    HR = 4.8*ones(1,length(stim_t));
    disp('Constant HR')
else
    % exponential
    HR1 = 4.8; HR2 = 6.2; t1 = 10e3; tau = 3*5e3;
    HR = HR2 - (HR2-HR1)*(stim_t<t1) - (HR2-HR1)*exp(-(stim_t-t1)/tau).*(stim_t>=t1);
    disp('HR modulation')
end

if ~isnumeric(APDMode)
    APDMode = str2num(APDMode);
end
if ~isnumeric(StimProtocol)
    StimProtocol = str2num(StimProtocol);
end
APD_modulation = 1;
if APDMode ==0
    APD_modulation = 0;
    APD_mod = 0.621*ones(1,length(stim_t));
    disp('Constant APD')
elseif APDMode == 1
    APD_modulation = 1;
    % increase and decrease (MOUSE default)
    APD_mod1 = 1; APD_mod2 = 1.26; t1 = 10e3; tau1 = 8e3; t2 = 40e3; tau2 = 6e3;
    APD_mod = APD_mod1 - (APD_mod2-APD_mod1)*exp(-(stim_t-t1)/tau1).*(stim_t>=t1) + (APD_mod2-APD_mod1)*1./(1+exp(+(stim_t-t2)/tau2)).*(stim_t>=t1);
    APD_mod = 0.621*APD_mod;
    disp('APD modulation - increase and decrease')
elseif APDMode ==2
    APD_modulation = 1;
    % exponential decrease (RABBIT default)
    APD_mod1 = 1; APD_mod2 = 0.8; t1 = 10e3; tau = 11e3;
    APD_mod = APD_mod2 - (APD_mod2-APD_mod1)*(stim_t<t1) - (APD_mod2-APD_mod1)*exp(-(stim_t-t1)/tau).*(stim_t>=t1);
    APD_mod = 0.621*APD_mod;
    disp('APD modulation - decrease (RABBIT)')
else
    disp(['Inappropriate selection for APDMode: 0, 1, or 2 accepted, received: ' num2str(APDMode) ])
end

exp_t = [-10 0 5 10 15 20 25 30 40 50 60]+10;
exp_t = exp_t*1000;
exp_apd80 = [47.52 47.52 52.18 56.5 57.98 56.64 55.1 53.28 49.6 48.24 46.54]/47.52;

Tms = 1000./HR; % ms

stim_duration = 5; % ms
%stim_amplitude = 9.5; % pA/pF

stim_init = zeros(1,length(stim_t));
stim = zeros(1,length(stim_t));

stim_init(1) = 1;
period = Tms(1);
next = Tms(1);
t0 = 0;
stim(1) = 1;

stim_t0 = zeros(1,length(stim_t));
stim_period = zeros(1,length(stim_t));
stim_hr = zeros(1,length(stim_t));

stim_t0(1) = 0;
stim_period(1) = Tms(1);
stim_hr(1) = HR(1);

stim_apd = zeros(1,length(stim_t));
stim_apd(1) = APD_mod(1);

for n=1+1:length(stim_t),
    if stim_t(n) < t0 + stim_duration,
        stim(n) = 1;
        stim_t0(n) = stim_t0(n-1);
        stim_period(n) = stim_period(n-1);
        stim_hr(n) = stim_hr(n-1);
        stim_apd(n) = stim_apd(n-1);
    end
    if stim_t(n) < next,
        stim_init(n) = 0;
        stim_t0(n) = stim_t0(n-1);
        stim_period(n) = stim_period(n-1);
        stim_hr(n) = stim_hr(n-1);
        stim_apd(n) = stim_apd(n-1);
    else
        stim_init(n) = 1;
        next = next + Tms(n);
        period = Tms(n);
        t0 = stim_t(n);
        stim(n) = 1;
        stim_t0(n) = t0;
        stim_period(n) = period;
        stim_hr(n) = 1000/period;
        stim_apd(n) = APD_mod(n);
    end
end
%% Assign initial conditions

%load yfin_WT_1Hz
%load yfin_WT_3Hz
% load yfin_WT_5Hz
load(initcond_datafile);
y0n = yfinal;
%% Run simulation

tic
tspan = [0 sim_duration];
options = odeset('RelTol',1e-5,'MaxStep',2);
[t,y] = ode15s(@morotti_et_al_mouse_masterODEfile,tspan,y0n,options, [p,StimProtocol]);
yfinal = y(end,:)';
toc
%% Save final conditions

%save yfin_WT_1Hz yfinal
%save yfin_WT_3Hz yfinal
%save yfin_WT_5Hz yfinal
%% Output variables

tArray = tArray(1:tStep);
Ica = I_Ca_store(1:tStep);
Ito = I_to_store(1,1:tStep);
Itof = I_to_store(2,1:tStep);
Itos = I_to_store(3,1:tStep);
INa = I_Na_store(1:tStep);
IK1 = I_K1_store(1:tStep);
s1 = gates(1,1:tStep);
k1 = gates(2,1:tStep);
Jserca = Jserca(1:tStep);
Iks = IKs_store(1:tStep);
Jleak = Jleak(1:tStep,:);
ICFTR = ICFTR(1:tStep);
Incx = Incx(1:tStep);
Ikur1 = I_kur1_store(1:tStep);
Ikur2 = I_kur2_store(1:tStep);
Iss = I_ss_store(1:tStep);
dVm = dVm_store(1:tStep);
Ipca = Ipca_store(1:tStep);
INaK = I_NaK_store(1:tStep);
INabk = I_Nabk_store(1:tStep);
Ikr = I_kr_store(1:tStep);
%% APD analysis

index_beat = find(stim_init==1);

time_beat = stim_t(index_beat(1:end-1)); % last stimulus excluded
period_beat = Tms(index_beat(1:end-1));
freq_beat = HR(index_beat(1:end-1));

APD90 = zeros(1,length(time_beat));
APperc = 90;

APD80 = zeros(1,length(time_beat));
APD50 = zeros(1,length(time_beat));
APD30 = zeros(1,length(time_beat));

Ca_syst = zeros(1,length(time_beat));
Ca_diast = zeros(1,length(time_beat));
CaT_amp = zeros(1,length(time_beat));
CaTt50 = zeros(1,length(time_beat));
CaTt63 = zeros(1,length(time_beat));

for n=1:length(time_beat),
    % Stimulation
    t1 = time_beat(n);
    t2 = time_beat(n)+period_beat(n)-5;
    % ROI t & Em
    ind1 = find(t>=t1);
    ind2 = find(t>=t2);
    t_roi = t(ind1(1):ind2(1))-t(ind1(1));
    Vm_roi = y(ind1(1):ind2(1),39);
    ind1a = find(tArray>=t1);
    ind2a = find(tArray>=t2);
    tArray_roi = tArray(ind1a(1):ind2a(1))-tArray(ind1a(1));
    dVm_roi = dVm(ind1a(1):ind2a(1));
    % APD analysis
    [dVmMax dVmMaxInd]=max(dVm_roi);
    tAP0=tArray_roi(dVmMaxInd);
    [VmMax VmMaxInd]=max(Vm_roi);
    %tAP0=t_roi(VmMaxInd);
    deltaVm=VmMax-min(Vm_roi);
    iAPD=find(Vm_roi(VmMaxInd:end)<VmMax-0.01*APperc*deltaVm);
    APD_ms=t_roi(VmMaxInd+iAPD(1))-tAP0;
    % Output
    APD90(n) = APD_ms;
    % Other APDs
    iAPD=find(Vm_roi(VmMaxInd:end)<VmMax-0.01*80*deltaVm);
    APD80(n)=t_roi(VmMaxInd+iAPD(1))-tAP0;
    iAPD=find(Vm_roi(VmMaxInd:end)<VmMax-0.01*50*deltaVm);
    APD50(n)=t_roi(VmMaxInd+iAPD(1))-tAP0;
    iAPD=find(Vm_roi(VmMaxInd:end)<VmMax-0.01*30*deltaVm);
    APD30(n)=t_roi(VmMaxInd+iAPD(1))-tAP0;
    % Ca
    Ca_roi = y(ind1(1):ind2(1),38);
    [CaMax CaMaxInd] = max(Ca_roi);
    Ca_syst(n) = CaMax;
    tCaMax = tArray_roi(CaMaxInd);
    Ca_diast(n) = min(Ca_roi);
    CaT_amp(n) = Ca_syst(n)-Ca_diast(n);
    % CaT decay
    iCaT=find(Ca_roi(CaMaxInd:end)<CaMax-0.01*50*CaT_amp(n));
    CaTt50(n)=t_roi(CaMaxInd+iCaT(1))-tCaMax;
    iCaT=find(Ca_roi(CaMaxInd:end)<CaMax-0.01*63*CaT_amp(n));
    CaTt63(n)=t_roi(CaMaxInd+iCaT(1))-tCaMax;
end
%% Save results
save('outputs.mat');

csvwrite('stimt.csv', stim_t'*1e-3)
csvwrite('APD80.csv', [time_beat'*1e-3 APD80'])
csvwrite('Na_i_conc.csv', [t y(:,34)])
csvwrite('CaTt.csv', [time_beat'*1e-3 CaTt63'])
csvwrite('freq_beat.csv', [time_beat'*1e-3 freq_beat'])
csvwrite('CaT_amp.csv', [time_beat'*1e-3 CaT_amp'])
csvwrite('Ca_syst.csv', [time_beat'*1e-3 Ca_syst'])
csvwrite('Ca_diast.csv', [time_beat'*1e-3 Ca_diast'])

filename = 'currents.csv';
varnames = 'tArray, Ica, Ito, Itof, Itos, INa, IK1, s1, k1, Jserca, Iks, Jleak1, Jleak2, ICFTR, Incx, Ikur1, Ikur2, Iss, dVm,  Ipca,  INaK,  INabk,  Ikr';
vardata = [tArray; Ica; Ito; Itof; Itos; INa; IK1; s1; k1; Jserca; Iks; Jleak(:,1)'; Jleak(:,2)'; ICFTR; Incx; Ikur1; Ikur2; Iss; dVm;  Ipca;  INaK;  INabk;  Ikr]';
fid = fopen(filename,'w');
fprintf(fid,'%s\r\n',varnames);
fclose(fid);
dlmwrite(filename, vardata,'-append','delimiter',',');

end
