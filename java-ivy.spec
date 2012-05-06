#
# Conditional build:
%bcond_without	javadoc		# don't build javadoc
%bcond_without	tests		# don't build and run tests

%define		srcname		ivy
%include	/usr/lib/rpm/macros.java
Summary:	Java-based dependency manager
Name:		java-%{srcname}
Version:	2.1.0
Release:	2
License:	ASL 2.0
Group:		Development/Tools
URL:		http://ant.apache.org/ivy/
Source0:	http://www.apache.org/dist/ant/ivy/%{version}/apache-%{srcname}-%{version}-src.tar.gz
# Source0-md5:	49130a0c8beb74d77653e5443dacecd5
BuildRequires:	ant
BuildRequires:	ant-nodeps
BuildRequires:	java-commons-httpclient
BuildRequires:	java-jsch
BuildRequires:	java-oro
BuildRequires:	jdk >= 1.5
BuildRequires:	jpackage-utils
BuildRequires:	rpmbuild(macros) >= 1.300
BuildRequires:	sed >= 4.0
Requires:	jpackage-utils
Provides:	ivy = %{version}-%{release}
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Apache Ivy is a tool for managing (recording, tracking, resolving and
reporting) project dependencies. It is designed as process agnostic
and is not tied to any methodology or structure. while available as a
standalone tool, Apache Ivy works particularly well with Apache Ant
providing a number of powerful Ant tasks ranging from dependency
resolution to dependency reporting and publication.

%package javadoc
Summary:	API Documentation for ivy
Group:		Development/Tools
Requires:	%{name} = %{version}-%{release}

%description javadoc
JavaDoc documentation for %{name}

%prep
%setup -q -n apache-%{srcname}-%{version}

# Fix messed-up encodings
for F in RELEASE_NOTES README LICENSE NOTICE CHANGES.txt; do
	sed 's/\r//' $F | iconv -f iso8859-1 -t utf8 > $F.utf8
	touch -r $F $F.utf8
	mv $F.utf8 $F
done

# Remove prebuilt documentation
rm -rf doc build/doc

# How to properly disable a plugin?
# we disable vfs plugin since commons-vfs is not available
rm -rf src/java/org/apache/ivy/plugins/repository/vfs \
		src/java/org/apache/ivy/plugins/resolver/VfsResolver.java
sed '/vfs.*=.*org.apache.ivy.plugins.resolver.VfsResolver/d' -i \
		src/java/org/apache/ivy/core/settings/typedef.properties

%build
# Craft class path
mkdir -p lib
build-jar-repository lib ant ant/ant-nodeps commons-httpclient oro jsch

# Build
%ant /localivy /offline jar %{?with_javadoc:javadoc}

%install
rm -rf $RPM_BUILD_ROOT

# Code
install -d $RPM_BUILD_ROOT%{_javadir}
install -p build/artifact/jars/%{srcname}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-%{version}.jar
ln -sf %{srcname}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}.jar

install -d $RPM_BUILD_ROOT%{_sysconfdir}/ant.d
echo "ivy" > $RPM_BUILD_ROOT%{_sysconfdir}/ant.d/%{srcname}

# API Documentation
%if %{with javadoc}
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -a build/doc/reports/api/. $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
ln -s %{srcname}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{srcname} # ghost symlink
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
ln -nfs %{srcname}-%{version} %{_javadocdir}/%{srcname}

%files
%defattr(644,root,root,755)
%doc RELEASE_NOTES CHANGES.txt LICENSE NOTICE README
%{_javadir}/*.jar

# %files -n ant-ivy
%{_sysconfdir}/ant.d/%{srcname}

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{srcname}-%{version}
%ghost %{_javadocdir}/%{srcname}
%endif
