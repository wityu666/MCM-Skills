function [x,t,U] = heat_cn(initial,C,L,T,nx,nt)
% Original constant-C heat equation CN, zero Dirichlet endpoints.
% U(:,k) is the field at t(k). This file is static, not MATLAB-run verified.
validateattributes(C,{'numeric'},{'real','scalar','finite','nonnegative'});
validateattributes(L,{'numeric'},{'real','scalar','finite','positive'});
validateattributes(T,{'numeric'},{'real','scalar','finite','positive'});
validateattributes(nx,{'numeric'},{'real','scalar','finite','integer','>=',2});
validateattributes(nt,{'numeric'},{'real','scalar','finite','integer','>=',1});
C=double(C); L=double(L); T=double(T); nx=double(nx); nt=double(nt);
x = linspace(0,L,nx+1).'; t = linspace(0,T,nt+1);
if isa(initial,'function_handle'), u0 = initial(x); else, u0 = initial; end
validateattributes(u0,{'numeric'},{'real','vector','finite','numel',nx+1});
u0 = double(u0(:));
tol = 64*eps*max(1,norm(u0,Inf));
if abs(u0(1))>tol || abs(u0(end))>tol
    error('heat_cn:boundary','This implementation requires zero endpoints.');
end
u0([1,end]) = 0;
dx = L/nx; dt = T/nt;
if dx<=0 || dt<=0, error('heat_cn:step','Step underflow; rescale units.'); end
% Binary decomposition avoids overflow/underflow in C*dt and dx^2.
if C==0
    r=0;
else
    [cm,ce]=log2(C); [tm,te]=log2(dt); [xm,xe]=log2(dx);
    r=pow2(cm*tm/(xm*xm),ce+te-2*xe);
end
if isnan(r) || isinf(r), error('heat_cn:ratio','Step ratio overflow.'); end
m = nx-1; one = ones(m,1);
A = spdiags([-r/2*one,(1+r)*one,-r/2*one],[-1,0,1],m,m);
B = spdiags([r/2*one,(1-r)*one,r/2*one],[-1,0,1],m,m);
U = zeros(nx+1,nt+1); U(:,1) = u0;
for k=1:nt
    rhs=B*U(2:nx,k);
    if any(isnan(rhs) | isinf(rhs)), error('heat_cn:rhs','Non-finite step RHS.'); end
    U(2:nx,k+1) = A\rhs;
end
if any(isnan(U(:)) | isinf(U(:))), error('heat_cn:finite','Non-finite field.'); end
end
