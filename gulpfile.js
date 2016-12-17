var concat = require('gulp-concat');
var gulp = require('gulp');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');

gulp.task('css', function() {
  return gulp.src('assets/scss/*.scss')
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        includePaths: 'node_modules',
      })
      .on('error', sass.logError)
    )
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/css/'));
});

gulp.task('js', function() {
  return gulp.src([
      'node_modules/jquery/dist/jquery.js',
      'node_modules/bootstrap/node_modules/tether/dist/js/tether.js',
      'node_modules/bootstrap/dist/js/bootstrap.js',
    ])
    .pipe(sourcemaps.init())
    .pipe(concat('debconf17.js'))
    .pipe(uglify())
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/js'));
});

gulp.task('assets', function() {
  return gulp.src('assets/{img,fonts}/**/*')
    .pipe(gulp.dest('static/'));
});

gulp.task('font-awesome', function() {
  return gulp.src('node_modules/font-awesome/fonts/*')
    .pipe(gulp.dest('static/fonts'));
});

gulp.task('watch', function() {
  gulp.watch('assets/js/*.js', ['js']);
  gulp.watch('assets/scss/*.scss', ['css']);
  gulp.watch('assets/img/*', ['assets']);
  gulp.watch('assets/fonts/*', ['assets']);
});

gulp.task('default', ['css', 'js', 'assets', 'font-awesome']);
