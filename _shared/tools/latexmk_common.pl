use File::Spec;
use JSON::PP qw(decode_json);

$pdf_mode = 4;
$lualatex = 'lualatex -synctex=1 -no-shell-escape %O %S';
$interaction = 'nonstopmode';
$halt_on_error = 1;
$file_line_error = 1;

sub lecture_cache_root {
    my ($product) = @_;
    return $ENV{'EXERCISE_SHEETS_CACHE'}
        if $product eq 'sheets' && $ENV{'EXERCISE_SHEETS_CACHE'};
    my $profile = $ENV{'USERPROFILE'} || $ENV{'HOME'}
        or die "Cannot determine the user profile for the build cache.\n";
    open my $settings, '<:raw', '../_shared/tools/cache_paths.json'
        or die "Cannot read the shared cache configuration: $!\n";
    my $paths = decode_json(do { local $/; <$settings> });
    close $settings;
    return File::Spec->catdir($profile, split('/', $paths->{$product}));
}

1;
