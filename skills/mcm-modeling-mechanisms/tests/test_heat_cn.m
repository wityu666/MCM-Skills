function test_heat_cn
% Small independent analytical/boundary checks; execution is logged separately.
fprintf('MATLAB_VERSION %s\n',version);
errors=zeros(1,2);
grids=[20,100;40,400];
for i=1:2
    [x,t,U]=heat_cn(@(x) sin(pi*x),.3,1,.2,grids(i,1),grids(i,2));
    exact=sin(pi*x)*exp(-.3*pi^2*t(end));
    errors(i)=max(abs(U(:,end)-exact));
    assert(all(U([1,end],:)==0,'all'));
end
assert(errors(2)<.001 && errors(1)/errors(2)>3.5 && errors(1)/errors(2)<4.5);
[~,~,U]=heat_cn([0;1;0],0,1e-200,1,2,1);
assert(isequal(U,[0,0;1,1;0,0]));
% One interior grid node has multiplier (1-r)/(1+r), r=4.
for inputs={[1e-300,1e-200,1e-100],[1e308,1e308,1e308]}
    args=inputs{1};
    [~,~,U]=heat_cn([0;1;0],args(1),args(2),args(3),2,1);
    assert(abs(U(2,end)+.6)<1e-13);
end
assert_rejects(@() heat_cn([0;1+100i;0],.3,1,.2,2,5));
assert_rejects(@() heat_cn('010',.3,1,.2,2,5));
assert_rejects(@() heat_cn([0,1;1,0],.3,1,.2,3,5));
assert_rejects(@() heat_cn([0;NaN;0],.3,1,.2,2,5));
assert_rejects(@() heat_cn([0;1;0],1e308,1e-100,1e308,2,1));
assert_rejects(@() heat_cn([0;1;0],.3,1,.2,Inf,1));
fprintf('MATLAB_HEAT_CN_TESTS_PASS\n');
end

function assert_rejects(call)
rejected=false;
try
    call();
catch
    rejected=true;
end
assert(rejected,'Expected invalid input to be rejected.');
end
